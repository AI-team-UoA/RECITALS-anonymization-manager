from fastapi.testclient import TestClient

from anonymization_manager.api import app

client = TestClient(app)


def test_health_returns_ok_without_token() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
