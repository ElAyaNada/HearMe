import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "hearme.db"


@contextmanager
def db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                voice_gender TEXT NOT NULL DEFAULT 'female',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def create_user(email: str, password_hash: str):
    # Lève sqlite3.IntegrityError si l'e-mail existe déjà
    with db() as conn:
        conn.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash),
        )


def get_user_by_email(email: str):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()


def update_voice(user_id: int, voice_gender: str):
    with db() as conn:
        conn.execute(
            "UPDATE users SET voice_gender = ? WHERE id = ?",
            (voice_gender, user_id),
        )