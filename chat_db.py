import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def init_chat_db():
    """Create the PostgreSQL chat schema if it does not already exist."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    session_id TEXT UNIQUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)

            cur.execute("""
                ALTER TABLE conversations
                ADD COLUMN IF NOT EXISTS session_id TEXT
            """)

            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS
                idx_conversations_session_id
                ON conversations(session_id)
                WHERE session_id IS NOT NULL
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER NOT NULL
                        REFERENCES conversations(id)
                        ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
                ON messages(conversation_id)
            """)

        conn.commit()


def create_conversation(title=None, session_id=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if session_id:
                cur.execute(
                    """
                    SELECT id
                    FROM conversations
                    WHERE session_id = %s
                    """,
                    (session_id,),
                )

                existing = cur.fetchone()

                if existing:
                    return existing[0]

            cur.execute(
                """
                INSERT INTO conversations (title, session_id)
                VALUES (%s, %s)
                RETURNING id
                """,
                (title, session_id),
            )

            conversation_id = cur.fetchone()[0]
            conn.commit()

            return conversation_id


def get_conversation_by_session_id(session_id):
    if not session_id:
        return None

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations
                WHERE session_id = %s
                """,
                (session_id,),
            )

            return cur.fetchone()


def save_message(conversation_id, role, content):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages
                    (conversation_id, role, content)
                VALUES
                    (%s, %s, %s)
                RETURNING id
                """,
                (conversation_id, role, content),
            )

            message_id = cur.fetchone()[0]

            cur.execute(
                """
                UPDATE conversations
                SET updated_at = NOW()
                WHERE id = %s
                """,
                (conversation_id,),
            )

            conn.commit()

            return message_id


def get_conversation_messages(conversation_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC
                """,
                (conversation_id,),
            )

            return cur.fetchall()


def get_conversation_history(conversation_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT role, content
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC
                """,
                (conversation_id,),
            )

            rows = cur.fetchall()

            return [
                {
                    "role": role,
                    "content": content,
                }
                for role, content in rows
            ]


def list_conversations():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations
                ORDER BY updated_at DESC
                """
            )

            return cur.fetchall()


def get_conversation(conversation_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM conversations
                WHERE id = %s
                """,
                (conversation_id,),
            )

            return cur.fetchone()

