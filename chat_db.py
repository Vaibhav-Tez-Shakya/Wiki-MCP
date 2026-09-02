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

            cur.execute("""
                ALTER TABLE messages
                ADD COLUMN IF NOT EXISTS turn_key TEXT
            """)

            # Normalize legacy duplicate turn keys before creating the
            # production-safe unique index. Existing messages are preserved;
            # only duplicate idempotency keys are cleared.
            cur.execute("""
                WITH ranked AS (
                    SELECT
                        id,
                        ROW_NUMBER() OVER (
                            PARTITION BY conversation_id, turn_key
                            ORDER BY id
                        ) AS rn
                    FROM messages
                    WHERE turn_key IS NOT NULL
                )
                UPDATE messages
                SET turn_key = NULL
                WHERE id IN (
                    SELECT id
                    FROM ranked
                    WHERE rn > 1
                )
            """)

            cur.execute("""
                DROP INDEX IF EXISTS idx_messages_conversation_turn_key
            """)

            cur.execute("""
                CREATE UNIQUE INDEX idx_messages_conversation_turn_key
                ON messages(conversation_id, turn_key)
            """)

        conn.commit()


def create_conversation(title=None, session_id=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if session_id:
                cur.execute(
                    """
                    INSERT INTO conversations (title, session_id)
                    VALUES (%s, %s)
                    ON CONFLICT (session_id)
                    DO UPDATE SET title = conversations.title
                    RETURNING id
                    """,
                    (title, session_id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO conversations (title, session_id)
                    VALUES (%s, NULL)
                    RETURNING id
                    """,
                    (title,),
                )

            conversation_id = cur.fetchone()[0]
            conn.commit()
            return conversation_id

def save_message(conversation_id, role, content, turn_key=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if turn_key is None:
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
            else:
                cur.execute(
                    """
                    INSERT INTO messages
                        (conversation_id, role, content, turn_key)
                    VALUES
                        (%s, %s, %s, %s)
                    ON CONFLICT (conversation_id, turn_key)
                    DO NOTHING
                    RETURNING id
                    """,
                    (conversation_id, role, content, turn_key),
                )

                row = cur.fetchone()

                if row is not None:
                    message_id = row[0]
                else:
                    cur.execute(
                        """
                        SELECT id
                        FROM messages
                        WHERE conversation_id = %s
                          AND turn_key = %s
                        """,
                        (conversation_id, turn_key),
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

