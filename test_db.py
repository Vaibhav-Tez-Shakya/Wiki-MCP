import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env")

try:
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT current_database(), current_user;
            """)

            database, user = cur.fetchone()

            print("Database connection successful!")
            print(f"Database: {database}")
            print(f"User: {user}")

except Exception as e:
    print("Database connection failed!")
    print(f"Error: {e}")