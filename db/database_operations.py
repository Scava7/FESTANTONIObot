import sqlite3
from config import DB_PATH
import os
from constants.constants import COLUMN_VOL, COLUMN_DISP


def get_connection():
    # Assicura che la cartella data/ esista
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        with open("db/schema.sql", "r") as f:
            conn.executescript(f.read())
        conn.commit()


def save_volunteer(user, name=None, last_name=None):
    with get_connection() as conn:
        conn.execute(f"""
            INSERT INTO volontari ({COLUMN_VOL.TELEGRAM_ID}, {COLUMN_VOL.NAME}, {COLUMN_VOL.LAST_NAME}, {COLUMN_VOL.USERNAME})
            VALUES (?, ?, ?, ?)
            ON CONFLICT({COLUMN_VOL.TELEGRAM_ID}) DO UPDATE SET
                {COLUMN_VOL.NAME} = excluded.{COLUMN_VOL.NAME},
                {COLUMN_VOL.LAST_NAME} = excluded.{COLUMN_VOL.LAST_NAME},
                {COLUMN_VOL.USERNAME} = excluded.{COLUMN_VOL.USERNAME}
        """, (user.id, name, last_name, user.username))
        conn.commit()


def volunteer_exists(user_id):
    with get_connection() as conn:
        cursor = conn.execute(f"SELECT 1 FROM volontari WHERE {COLUMN_VOL.TELEGRAM_ID} = ?", (user_id,))
        return cursor.fetchone() is not None


def increment_command_count(user_id, column):
    with get_connection() as conn:
        conn.execute(f"""
            UPDATE volontari
            SET {column} = {column} + 1
            WHERE {COLUMN_VOL.TELEGRAM_ID} = ?
        """, (user_id,))
        conn.commit()


def increment_unknown_count(user_id):
    increment_command_count(user_id, COLUMN_VOL.UNKNOWN)


def save_availability(user_id, giorno, fascia):
    with get_connection() as conn:
        conn.execute(f"""
            INSERT OR IGNORE INTO disponibilita ({COLUMN_DISP.TELEGRAM_ID}, {COLUMN_DISP.DISP_GIORNO}, {COLUMN_DISP.DISP_FASCIA})
            VALUES (?, ?, ?)
        """, (user_id, giorno, fascia))
        conn.commit()


def get_user_info(user_id):
    with get_connection() as conn:
        cursor = conn.execute(f"""
            SELECT {COLUMN_VOL.NAME}, {COLUMN_VOL.LAST_NAME}, {COLUMN_VOL.USERNAME}
            FROM volontari
            WHERE {COLUMN_VOL.TELEGRAM_ID} = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                "name": row[0],
                "last_name": row[1],
                "username": row[2]
            }
        return {}


def get_user_availabilities(user_id):
    with get_connection() as conn:
        cursor = conn.execute(f"""
            SELECT {COLUMN_DISP.DISP_GIORNO}, {COLUMN_DISP.DISP_FASCIA} FROM disponibilita
            WHERE {COLUMN_DISP.TELEGRAM_ID} = ?
            ORDER BY {COLUMN_DISP.DISP_GIORNO}, {COLUMN_DISP.DISP_FASCIA}
        """, (user_id,))
        return cursor.fetchall()


def get_all_availabilities_with_names():
    with get_connection() as conn:
        cursor = conn.execute(f"""
            SELECT v.{COLUMN_VOL.NAME}, v.{COLUMN_VOL.LAST_NAME}, v.{COLUMN_VOL.USERNAME},
                   d.{COLUMN_DISP.DISP_GIORNO}, d.{COLUMN_DISP.DISP_FASCIA}
            FROM disponibilita d
            JOIN volontari v ON d.{COLUMN_DISP.TELEGRAM_ID} = v.{COLUMN_VOL.TELEGRAM_ID}
            ORDER BY d.{COLUMN_DISP.DISP_GIORNO}, d.{COLUMN_DISP.DISP_FASCIA}
        """)
        return cursor.fetchall()
