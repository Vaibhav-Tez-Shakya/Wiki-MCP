import os
import time
from typing import Any

import jwt

from mcp.server.auth.provider import AccessToken, TokenVerifier


class Auth0TokenVerifier(TokenVerifier):
    """
    Validates Auth0 RS256 access tokens for the MCP resource server.

    Validation performed:
    - JWT signature using Auth0 JWKS
    - RS256 algorithm
    - issuer
    - audience
    - required JWT time claims
    - expiration
    - OAuth scopes
    - Auth0 RBAC permissions
    """

    def __init__(self) -> None:
        self.domain = os.environ["AUTH0_DOMAIN"].rstrip("/")

        self.issuer = os.getenv(
            "AUTH0_ISSUER",
            f"https://{self.domain}/",
        )

        self.audience = os.environ["AUTH0_AUDIENCE"]

        self.jwks_url = (
            f"https://{self.domain}/.well-known/jwks.json"
        )

        self._jwks_client = jwt.PyJWKClient(
            self.jwks_url
        )

    async def verify_token(
        self,
        token: str,
    ) -> AccessToken | None:

        try:
            signing_key = (
                self._jwks_client.get_signing_key_from_jwt(token)
            )

            payload: dict[str, Any] = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "require": [
                        "exp",
                        "iat",
                        "iss",
                        "aud",
                    ],
                },
            )

            expires_at = payload.get("exp")

            if expires_at is not None:
                if int(expires_at) <= int(time.time()):
                    print(
                        "AUTH0 TOKEN REJECTED: token expired",
                        flush=True,
                    )
                    return None

            scopes: set[str] = set()

            # Standard OAuth scope claim.
            scope_claim = payload.get("scope", "")

            if isinstance(scope_claim, str):
                scopes.update(
                    scope
                    for scope in scope_claim.split()
                    if scope
                )

            elif isinstance(scope_claim, list):
                scopes.update(
                    str(scope)
                    for scope in scope_claim
                    if scope
                )

            # Auth0 RBAC permissions claim.
            permissions_claim = payload.get(
                "permissions",
                [],
            )

            if isinstance(permissions_claim, list):
                scopes.update(
                    str(permission)
                    for permission in permissions_claim
                    if permission
                )

            client_id = str(
                payload.get("azp")
                or payload.get("client_id")
                or "auth0"
            )

            subject = payload.get("sub")

            return AccessToken(
                token=token,
                client_id=client_id,
                scopes=sorted(scopes),
                expires_at=(
                    int(expires_at)
                    if expires_at is not None
                    else None
                ),
                resource=self.audience,
                subject=(
                    str(subject)
                    if subject is not None
                    else None
                ),
                claims=payload,
            )

        except Exception as exc:
            print(
                "AUTH0 TOKEN VERIFICATION FAILED: "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )
            return None
