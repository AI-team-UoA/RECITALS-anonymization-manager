import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from anonymization_manager import auth
from anonymization_manager.api import app

client = TestClient(app, raise_server_exceptions=False)

ISSUER = "http://keycloak.test/realms/recitals"
AUDIENCE = "recitals-anonymization-manager"

# Keycloak signing key.
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Fails validation, a request that passes
INVALID_BODY = {"k": 0}


@pytest.fixture(autouse=True)
def keycloak(monkeypatch):
    """Configures auth for a fake Keycloak whose public key is KEY's."""
    monkeypatch.setenv(auth.ISSUER_ENV, ISSUER)
    monkeypatch.delenv(auth.AUDIENCE_ENV, raising=False)
    monkeypatch.delenv(auth.PERMISSION_ENV, raising=False)
    auth.get_settings.cache_clear()
    monkeypatch.setattr(auth, "_signing_key", lambda token: KEY.public_key())
    yield
    auth.get_settings.cache_clear()


def _token(key=KEY, roles=("anon.execute",), scope="", **overrides) -> str:
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "service-account-compliance-manager",
        "azp": "recitals-compliance-manager",
        "exp": int(time.time())+300,
        "scope": scope,
        "resource_access": {AUDIENCE: {"roles": list(roles)}}
    }
    claims.update(overrides)
    return jwt.encode(claims, key, algorithm="RS256")

def _post(token: str | None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.post("/anonymize", json=INVALID_BODY, headers=headers)

def test_valid_token_is_accepted() -> None:
    response = _post(_token())

    assert response.status_code == 400
    assert response.json()["error"] == "ValidationError"

def test_permission_as_scope_is_accepted() -> None:
    response = _post(_token(roles=(), scope="openid anon.execute"))

    assert response.status_code == 400

def test_missing_token_returns_401() -> None:
    response = _post(None)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json() == {
        "error": "Unauthorized",
        "detail": "Missing bearer token.",
    }


@pytest.mark.parametrize(
    "token",
    [
        _token(exp=int(time.time())-3600),
        _token(iss="http://hacker.test/realms/recitals"),
        _token(aud="recitals-cryptography-manager"),
        _token(key=OTHER_KEY),
        "not-a-jwt"
    ],
    ids=["expired", "wrong-issuer", "wrong-audience", "wrong-signature", "garbage"],
)
def test_invalid_token_returns_401(token) -> None:
    response = _post(token)

    assert response.status_code == 401
    assert response.json()["error"] == "Unauthorized"


def test_missing_permission_returns_403() -> None:
    response = _post(_token(roles=("something.else",)))

    assert response.status_code == 403
    assert response.json() == {
        "error": "Forbidden",
        "detail": "Missing required permission `anon.execute`."
    }

def test_role_on_another_client_is_ignored() -> None:
    token = _token(
        roles=(),
        resource_access={"recitals-cryptography-manager": {"roles": ["anon.execute"]}}
    )

    assert _post(token).status_code == 403

def test_permission_name_is_configurable(monkeypatch) -> None:
    monkeypatch.setenv(auth.PERMISSION_ENV, "execute")
    auth.get_settings.cache_clear()

    assert _post(_token(roles=("execute",))).status_code == 400
    assert _post(_token(roles=("anon.execute",))).status_code == 403

def test_keycloak_unreachable_returns_503(monkeypatch) -> None:
    def unreachable(token):
        raise jwt.PyJWKClientConnectionError("connection refused")

    monkeypatch.setattr(auth, "_signing_key", unreachable)

    response = _post(_token())

    assert response.status_code == 503
    assert response.json()["error"] == "ServiceUnavailable"


