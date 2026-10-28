from fastapi.testclient import TestClient

from anonymization_manager.api import app
from anonymization_manager.core import AnonymizationManager
from tests.common import *

client = TestClient(app, raise_server_exceptions=False)

@pytest.fixture(scope="module")
def small_data(tmp_path_factory) -> str:
    """A 1000-row copy of the adult dataset"""
    path = tmp_path_factory.mktemp("data")/"adult_small.csv"
    with open(PATH) as src:
        lines = [next(src) for _ in range(1001)]
    path.write_text("".join(lines))
    return str(path)

def _valid_body(**overrides) -> dict:
    body = {
        "data": PATH,
        "quasi_identifiers": ["age", "sex"],
        "hierarchies": {"age": AGE_PATH, "sex": SEX_PATH},
        "k":2,
    }
    body.update(overrides)
    return body

def _fail_with(monkeypatch, error: Exception) -> None:
    """Makes AnonymizationManager.anonymize raise the given error."""
    def fake_anonymize(config):
        raise error

    monkeypatch.setattr(AnonymizationManager, "anonymize", fake_anonymize)


class TestSuccess:
    @pytest.mark.parametrize("backend", ["arx", "anjana"])
    def test_valid_request_returns_200(self, small_data, backend) -> None:
        body = _valid_body(data=small_data, backend=backend)
        response = client.post("/anonymize", json=body)

        assert response.status_code == 200
        content = response.json()
        assert len(content["data"]) > 0
        assert set(content["metadata"]) == {
            "anonymization_time_ms",
            "average_equivalence_class_size",
            "transformations",
        }

class TestValidationErrors:
    @pytest.mark.parametrize(
        "overrides, field",
        [
            ({"k":0}, "k"),
            ({"t":1.5}, "t"),
            ({"backend": "foo"}, "backend"),
            ({"data": "does/not/exist.csv"}, "data"),
        ],
    )
    def test_invalid_config_returns_400(self, overrides, field) -> None:
        response = client.post("/anonymize", json=_valid_body(**overrides))

        assert response.status_code == 400
        content = response.json()
        assert content["error"] == "ValidationError"
        assert field in [err["field"] for err in content["detail"]]

    def test_missing_hierarchy_returns_400(self) -> None:
        body = _valid_body(hierarchies={"age": "missing.csv", "sex": SEX_PATH})
        response = client.post("/anonymize", json=body)

        assert response.status_code == 400
        messages = [err["message"] for err in response.json()["detail"]]
        assert any("missing.csv" in m for m in messages)

    def test_missing_data_returns_400(self) -> None:
        response = client.post("/anonymize", json={"k":2})

        assert response.status_code == 400
        assert response.json()["detail"] == [
            {"field": "data", "message": "Field required"}
        ]

    def test_all_field_errors_are_reported(self) -> None:
        response = client.post("/anonymize", json=_valid_body(k=0, t=1.5))

        fields = [err["field"] for err in response.json()["detail"]]
        assert "k" in fields and "t" in fields

    def test_value_error_prefix_is_removed(self) -> None:
        body = _valid_body(data="does/not/exists.csv")
        response = client.post("/anonymize", json=body)

        for err in response.json()["detail"]:
            assert not err["message"].startswith("Value error, ")

class TestAnonymizationErrors:
    def test_configuration_error_returns_400(self, monkeypatch) -> None:
        _fail_with(monkeypatch, ConfigurationError("bad metric", backend="arx"))

        response = client.post("/anonymize", json=_valid_body())

        assert response.status_code == 400
        assert response.json() == {
            "error": "ConfigurationError",
            "detail": "bad metric",
            "backend": "arx"
        }

    @pytest.mark.parametrize("backend", ["arx", "anjana"])
    def test_no_solution_returns_422(self, small_data, backend) -> None:
        # salary-class has only 2 distinct values, so l=7 is impossible.
        body = {
            "data": small_data,
            "quasi_identifiers": ["age", "sex"],
            "sensitive_attributes": ["salary-class"],
            "hierarchies": {"age": AGE_PATH, "sex": SEX_PATH},
            "l": 7,
            "suppression_limit": 0.5,
            "backend": backend,
        }
        response = client.post("/anonymize", json=body)

        assert response.status_code == 422
        content = response.json()
        assert content["error"] == "NoSolutionError"
        assert content["backend"] == backend

    def test_backend_error_returns_500(self, monkeypatch) -> None:
        _fail_with(monkeypatch, BackendError("JVM crashed", backend="arx"))

        response = client.post("/anonymize", json=_valid_body())

        assert response.status_code == 500
        assert response.json() == {
            "error": "BackendError",
            "detail": "JVM crashed",
            "backend": "arx",
        }

    def test_unexpected_error_hides_details(self, monkeypatch) -> None:
        _fail_with(monkeypatch, RuntimeError("secret server side error"))

        response = client.post("/anonymize", json=_valid_body())

        assert response.status_code == 500
        assert response.json() == {
            "error": "InternalServerError",
            "detail": "An unexpected error occurred.",
        }
        assert "secret" not in response.text