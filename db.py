import os
import psycopg2
import psycopg2.extras

DB_URL = os.environ.get("NEON_DATABASE_URL")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS submissions (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  category TEXT NOT NULL,
  message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

INSERT_SQL = """
INSERT INTO submissions (name, email, category, message)
VALUES (%s, %s, %s, %s)
RETURNING id;
"""

SELECT_LATEST_SQL = """
SELECT id, name, email, category, message, created_at
FROM submissions
ORDER BY id DESC
LIMIT %s;
"""

def get_conn():
    import os
    import streamlit as st
    import psycopg2

    db_url = os.getenv("NEON_DATABASE_URL") or st.secrets.get("NEON_DATABASE_URL")

    if not db_url:
        raise ValueError("NEON_DATABASE_URL is not set in Streamlit Secrets")

    return psycopg2.connect(db_url)



def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)

def insert_submission(name: str, email: str, category: str, message: str) -> int:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(INSERT_SQL, (name, email, category, message))
            new_id = cur.fetchone()[0]
            return int(new_id)

def fetch_latest(limit: int = 50):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(SELECT_LATEST_SQL, (limit,))
            return cur.fetchall()