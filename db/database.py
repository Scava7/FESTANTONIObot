import sqlite3
from config import DB_PATH
import os
from constants.constants import COLUMN


def get_connection():
    # Assicura che la cartella data/ esista
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        with open("db/schema.sql", "r") as f:
            conn.executescript(f.read())
        # Crea anche la tabella disponibilita se non esiste
        conn.execute("""
            CREATE TABLE IF NOT EXISTS disponibilita (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                giorno TEXT NOT NULL,
                fascia TEXT NOT NULL,
                UNIQUE(telegram_id, giorno, fascia)
            )
        """)
        conn.commit()


def save_volunteer(user, name=None, last_name=None):
    with get_connection() as conn:
        conn.execute(f"""
            INSERT INTO volontari (telegram_id, first_name, last_name, username)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                username = excluded.username
        """, (user.id, name, last_name, user.username))
        conn.commit()


def volunteer_exists(user_id):
    with get_connection() as conn:
        cursor = conn.execute("SELECT 1 FROM volontari WHERE telegram_id = ?", (user_id,))
        return cursor.fetchone() is not None


def increment_command_count(user_id, column):
    with get_connection() as conn:
        conn.execute(f"""
            UPDATE volontari
            SET {column} = {column} + 1
            WHERE telegram_id = ?
        """, (user_id,))
        conn.commit()


def increment_unknown_count(user_id):
    increment_command_count(user_id, COLUMN.UNKNOWN)


def safe_add_column(column_name, column_def):
    with get_connection() as conn:
        cursor = conn.execute("PRAGMA table_info(volontari)")
        columns = [row[1] for row in cursor.fetchall()]
        if column_name not in columns:
            conn.execute(f"ALTER TABLE volontari ADD COLUMN {column_name} {column_def}")
            conn.commit()


def update_schema():
    safe_add_column(COLUMN.N_CMD_START, "INTEGER DEFAULT 0")
    safe_add_column(COLUMN.N_CMD_REGISTR, "INTEGER DEFAULT 0")
    safe_add_column(COLUMN.UNKNOWN, "INTEGER DEFAULT 0")
    safe_add_column(COLUMN.NAME, "TEXT")
    safe_add_column(COLUMN.LAST_NAME, "TEXT")
    safe_add_column(COLUMN.USERNAME, "TEXT")


def save_availability(user_id, giorno, fascia):
    with get_connection() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO disponibilita (telegram_id, giorno, fascia)
            VALUES (?, ?, ?)
        """, (user_id, giorno, fascia))
        conn.commit()

def get_user_info(user_id):
    with get_connection() as conn:
        cursor = conn.execute(f"""
            SELECT {COLUMN.NAME}, {COLUMN.LAST_NAME}, {COLUMN.USERNAME}
            FROM volontari
            WHERE telegram_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                "name": row[0],
                "last_name": row[1],
                "username": row[2]
            }
        return {}