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

def volunteer_exists(user_id):
    with get_connection() as conn:
        cursor = conn.execute("SELECT 1 FROM volontari WHERE telegram_id = ?", (user_id,))
        return cursor.fetchone() is not None

def safe_add_column(column_name, column_def):
    with get_connection() as conn:
        cursor = conn.execute("PRAGMA table_info(volontari)")
        columns = [row[1] for row in cursor.fetchall()]
        if column_name not in columns:
            conn.execute(f"ALTER TABLE volontari ADD COLUMN {column_name} {column_def}")
            conn.commit()

def update_schema():
    safe_add_column("start_cmd_used", "INTEGER DEFAULT 0")
    safe_add_column("messaggi_non_riconosciuti", "INTEGER DEFAULT 0")

def increment_command_count(user_id):
    with get_connection() as conn:
        conn.execute("""
            UPDATE volontari
            SET start_cmd_used = start_cmd_used + 1
            WHERE telegram_id = ?
        """, (user_id,))
        conn.commit()


def increment_unknown_count(user_id):
    with get_connection() as conn:
        conn.execute("""
            UPDATE volontari
            SET messaggi_non_riconosciuti = messaggi_non_riconosciuti + 1
            WHERE telegram_id = ?
        """, (user_id,))
        conn.commit()
