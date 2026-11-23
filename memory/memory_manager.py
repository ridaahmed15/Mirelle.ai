
import sqlite3
from pathlib import Path


class MemoryManager:

    def __init__(self):
        self.db_path = (
            Path(__file__).parent / "storage" / "mirelle.db"
        )

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.create_tables()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        with self.connect() as conn:

            # Conversation history
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Smart memory: important facts
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact_key TEXT UNIQUE NOT NULL,
                    fact_value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    # ---------------------------
    # CHAT HISTORY
    # ---------------------------

    def save_message(self, role, content):
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO chat_history (role, content) VALUES (?, ?)",
                (role, content)
            )

    def load_recent_messages(self, limit=20):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content
                FROM chat_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,)
            ).fetchall()

        rows.reverse()

        return [
            {"role": role, "content": content}
            for role, content in rows
        ]

    def clear_history(self):
        with self.connect() as conn:
            conn.execute("DELETE FROM chat_history")

    # ---------------------------
    # SMART MEMORY
    # ---------------------------

    def save_fact(self, key, value):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO user_facts (fact_key, fact_value)
                VALUES (?, ?)
                ON CONFLICT(fact_key)
                DO UPDATE SET
                    fact_value = excluded.fact_value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, value)
            )

    def get_facts(self):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT fact_key, fact_value
                FROM user_facts
                ORDER BY fact_key
                """
            ).fetchall()

        return [
            {"key": key, "value": value}
            for key, value in rows
        ]

    def delete_fact(self, key):
        with self.connect() as conn:
            conn.execute(
                "DELETE FROM user_facts WHERE fact_key = ?",
                (key,)
            )
