"""
Token validation for the REST API.

The API is an OAuth 2.0 resource server for the RECITALS Keycloak.

Settings (environment variables):
    ANONYMIZATION_MANAGER_OIDC_ISSUER               required, e.g. http://localhost:8080/realms/recitals
    ANONYMIZATION_MANAGER_OIDC_JWKS_URL             default: <issuer>/protocol/openid-connect/certs
    ANONYMIZATION_MANAGER_OIDC_AUDIENCE             default: recitals-anonymization-manager
    ANONYMIZATION_MANAGER_REQUIRED_PERMISSION       default: anon.execute

Tokens are never logged.
"""

import os
from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

ISSUER_ENV = "ANONYMIZATION_MANAGER_OIDC_ISSUER"
JWKS_URL_ENV = "ANONYMIZATION_MANAGER_OIDC_JWKS_URL"
AUDIENCE_ENV = "ANONYMIZATION_MANAGER_OIDC_AUDIENCE"
PERMISSION_ENV = "ANONYMIZATION_MANAGER_REQUIRED_PERMISSION"
DEFAULT_AUDIENCE = "recitals-anonymization-manager"
DEFAULT_PERMISSION = "anon.execute"

_bearer = HTTPBearer(auto_error=False)

class AuthError(Exception):
    """
    An authentication request was rejected.

    401: Missing or invalid token.
    403: Valid token without permission.
    503: Keycloak could not be reached.
    """

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

@dataclass(frozen=True)
class Caller:
    """The authenticated user or service behind a request."""

    subject: str # who the token belongs to
    client: str | None # "azp": which Keycloak client obtained it
    permissions: frozenset[str]

@dataclass(frozen=True)
class Settings:
    issuer: str
    jwks_url: str
    audience: str
    permission: str

@lru_cache
def get_settings() -> Settings:
    """Reads the settings from the environment, once."""

    issuer = os.getenv(ISSUER_ENV)
    if not issuer:
        raise RuntimeError(f"{ISSUER_ENV} is not set")
    
    issuer = issuer.rstrip("/")
    return Settings(
        issuer=issuer,
        jwks_url=os.getenv(JWKS_URL_ENV, f"{issuer}/protocol/openid-connect/certs"),
        audience=os.getenv(AUDIENCE_ENV, DEFAULT_AUDIENCE),
        permission=os.getenv(PERMISSION_ENV, DEFAULT_PERMISSION),
    )

@lru_cache
def _jwks_client() -> jwt.PyJWKClient:
    # Keys are cached, a token signed with an unknown key makes the client fetch the key again.
    return jwt.PyJWKClient(get_settings().jwks_url, cache_keys=True, lifespan=300)

def _signing_key(token: str):
    """Grabs and returns Keycloak's public key that signed the token."""
    return _jwks_client().get_signing_key_from_jwt(token).key

def authenticate(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)
) -> Caller:
    """Validates the bearer token and returns the caller."""
    if credentials is None:
        raise AuthError(401, "Missing bearer token.")

    settings = get_settings()
    token = credentials.credentials
    try:
        claims = jwt.decode(
            token,
            _signing_key(token),
            algorithms=["RS256"],
            audience=settings.audience,
            issuer=settings.issuer,
            options={"require": ["exp", "iss", "aud", "sub"]},
            leeway=30,
        )
    except jwt.PyJWKClientConnectionError as ex:
        raise AuthError(503, "Identity provider is unavailable.") from ex
    except jwt.PyJWTError as ex:
        raise AuthError(401, f"Invalid token: {ex}") from ex

    # The permission can come as a scope or as a role.
    scopes = set(claims.get("scope", "").split())
    roles = set(
        claims.get("resource_access", {}).get(settings.audience, {}).get("roles", [])
    )

    return Caller(
        subject=claims["sub"],
        client=claims.get("azp"),
        permissions=frozenset(scopes | roles)
    )

def require_permission(caller: Caller = Depends(authenticate)) -> Caller:
    """Allows only callers with permission."""

    permission = get_settings().permission
    if permission not in caller.permissions:
        raise AuthError(403, f"Missing required permission `{permission}`.")

    return caller
