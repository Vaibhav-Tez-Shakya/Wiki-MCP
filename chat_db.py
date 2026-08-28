import os

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def get_connection():
    return psycopg.connect(DATABASE_URL)


def create_conversation(title=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (title)
                VALUES (%s)
                RETURNING id
                """,
                (title,),
            )

            conversation_id = cur.fetchone()[0]
            conn.commit()

            return conversation_id


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