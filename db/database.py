import sqlite3
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        with open("db/schema.sql", "r") as f:
            conn.executescript(f.read())

def save_volunteer(user):
    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO volontari (telegram_id, first_name, last_name, username)
            VALUES (?, ?, ?, ?)
        """, (user.id, user.first_name, user.last_name, user.username))
        conn.commit()