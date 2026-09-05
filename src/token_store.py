import os
import hashlib
import secrets
from typing import Any

import psycopg


TOKEN_PREFIX = "wk_"
TOKEN_DATABASE_URL = os.environ["TOKEN_DATABASE_URL"]


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def init_token_db() -> None:
    with psycopg.connect(TOKEN_DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL DEFAULT 'active',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    revoked_at TIMESTAMPTZ NULL
                )
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_user_tokens_user_id
                ON user_tokens(user_id)
                """
            )

            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_user_tokens_status
                ON user_tokens(status)
                """
            )

        conn.commit()


def generate_token() -> str:
    return TOKEN_PREFIX + secrets.token_urlsafe(32)


def create_user_token(user_id: str) -> str:
    token = generate_token()
    token_hash = _hash_token(token)

    with psycopg.connect(TOKEN_DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_tokens
                    (user_id, token_hash, status)
                VALUES
                    (%s, %s, 'active')
                """,
                (user_id, token_hash),
            )

        conn.commit()

    return token


def validate_user_token(token: str) -> dict[str, Any] | None:
    if not token.startswith(TOKEN_PREFIX):
        return None

    token_hash = _hash_token(token)

    with psycopg.connect(TOKEN_DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, user_id, status, created_at, revoked_at
                FROM user_tokens
                WHERE token_hash = %s
                LIMIT 1
                """,
                (token_hash,),
            )

            row = cur.fetchone()

    if row is None:
        return None

    token_id, user_id, status, created_at, revoked_at = row

    if status != "active":
        return None

    return {
        "id": token_id,
        "user_id": user_id,
        "status": status,
        "created_at": created_at,
        "revoked_at": revoked_at,
    }


def revoke_user_token(token_id: int) -> bool:
    with psycopg.connect(TOKEN_DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE user_tokens
                SET
                    status = 'revoked',
                    revoked_at = NOW()
                WHERE id = %s
                  AND status = 'active'
                """,
                (token_id,),
            )

            changed = cur.rowcount > 0

        conn.commit()

    return changed


def list_user_tokens() -> list[tuple[Any, ...]]:
    with psycopg.connect(TOKEN_DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    user_id,
                    status,
                    created_at,
                    revoked_at
                FROM user_tokens
                ORDER BY id
                """
            )

            return cur.fetchall()
