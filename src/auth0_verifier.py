import os
import time
from typing import Any

import jwt

from mcp.server.auth.provider import AccessToken, TokenVerifier

from token_store import init_token_db, validate_user_token


class Auth0TokenVerifier(TokenVerifier):
    """
    Validates both:

    1. Revocable Wiki MCP user tokens.
    2. Auth0 RS256 OAuth access tokens.

    User tokens are opaque bearer credentials beginning with "wk_".
    Auth0 JWT validation remains unchanged.
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

        # Create the revocable-token table if it does not exist.
        init_token_db()

    async def verify_token(
        self,
        token: str,
    ) -> AccessToken | None:

        # ---------------------------------------------------------
        # 1. Check our revocable user token first.
        # ---------------------------------------------------------

        if token.startswith("wk_"):
            user_token = validate_user_token(token)

            if user_token is None:
                print(
                    "USER TOKEN REJECTED: invalid or revoked token",
                    flush=True,
                )
                return None

            print(
                "USER TOKEN ACCEPTED:",
                {
                    "token_id": user_token["id"],
                    "user_id": user_token["user_id"],
                },
                flush=True,
            )

            return AccessToken(
                token=token,
                client_id=f"user-token-{user_token['id']}",
                scopes=["read:wiki"],
                expires_at=None,
                resource=self.audience,
                subject=str(user_token["user_id"]),
                claims={
                    "auth_type": "user_token",
                    "token_id": user_token["id"],
                    "user_id": user_token["user_id"],
                },
            )

        # ---------------------------------------------------------
        # 2. Existing Auth0 JWT validation.
        # ---------------------------------------------------------

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

            print(
                "AUTH0 TOKEN CLAIMS:",
                {
                    "iss": payload.get("iss"),
                    "aud": payload.get("aud"),
                    "scope": payload.get("scope"),
                    "permissions": payload.get("permissions"),
                    "azp": payload.get("azp"),
                    "sub": payload.get("sub"),
                },
                flush=True,
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
