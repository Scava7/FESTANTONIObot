
from config import ENABLE_TERMINAL_DEBUG
from constants.constants import COLUMN_VOL, COLUMN_DISP
from db.connection import get_connection, get_mysql_connection

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

    try:
        with get_mysql_connection() as mysql_conn:
            mysql_cursor = mysql_conn.cursor()
            mysql_cursor.execute("""
                INSERT INTO volontari (telegram_id, first_name, last_name, telegram_username)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    first_name = VALUES(first_name),
                    last_name = VALUES(last_name),
                    telegram_username = VALUES(telegram_username)
            """, (user.id, name, last_name, user.username))
            if ENABLE_TERMINAL_DEBUG:
                print(f"[DEBUG] MySQL save_volunteer: Telegram ID {user.id} inserito/aggiornato")
    except Exception as e:
        if ENABLE_TERMINAL_DEBUG:
            print(f"[ERROR] MySQL save_volunteer: Telegram ID {user.id} - Errore: {e}")

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

    try:
        with get_mysql_connection() as mysql_conn:
            mysql_cursor = mysql_conn.cursor()
            mysql_cursor.execute(f"""
                UPDATE volontari
                SET {column} = {column} + 1
                WHERE telegram_id = %s
            """, (user_id,))
            if ENABLE_TERMINAL_DEBUG:
                print(f"[DEBUG] MySQL increment_command_count: Telegram ID {user_id} incrementato colonna {column}")
    except Exception as e:
        if ENABLE_TERMINAL_DEBUG:
            print(f"[ERROR] MySQL increment_command_count: Telegram ID {user_id} - Errore: {e}")

def increment_unknown_count(user_id):
    increment_command_count(user_id, COLUMN_VOL.UNKNOWN)

def save_availability(user_id, giorno, fascia, nome_cognome=None):
    with get_connection() as conn:
        conn.execute(f"""
            INSERT OR IGNORE INTO disponibilita ({COLUMN_DISP.TELEGRAM_ID}, {COLUMN_DISP.DISP_GIORNO}, {COLUMN_DISP.DISP_FASCIA}, {COLUMN_DISP.DISP_NOMECOGNOME})
            VALUES (?, ?, ?, ?)
        """, (user_id, giorno, fascia, nome_cognome))
        conn.commit()

    try:
        with get_mysql_connection() as mysql_conn:
            mysql_cursor = mysql_conn.cursor()
            mysql_cursor.execute("""
                INSERT INTO disponibilita (telegram_id, giorno, fascia, nome_cognome)
                VALUES (%s, %s, %s, %s)
            """, (user_id, giorno, fascia, nome_cognome))
            if ENABLE_TERMINAL_DEBUG:
                print(f"[DEBUG] MySQL save_availability: Disponibilità salvata per Telegram ID {user_id}, Giorno {giorno}, Fascia {fascia}")
    except Exception as e:
        if ENABLE_TERMINAL_DEBUG:
            print(f"[ERROR] MySQL save_availability: Telegram ID {user_id} - Errore: {e}")

def delete_availabilities_for_user(user_id):
    with get_connection() as conn:
        conn.execute(f"""
            DELETE FROM disponibilita
            WHERE {COLUMN_DISP.TELEGRAM_ID} = ?
        """, (user_id,))
        conn.commit()

    try:
        with get_mysql_connection() as mysql_conn:
            mysql_cursor = mysql_conn.cursor()
            mysql_cursor.execute("""
                DELETE FROM disponibilita
                WHERE telegram_id = %s
            """, (user_id,))
            if ENABLE_TERMINAL_DEBUG:
                print(f"[DEBUG] MySQL delete_availabilities_for_user: Cancellate disponibilità per Telegram ID {user_id}")
    except Exception as e:
        if ENABLE_TERMINAL_DEBUG:
            print(f"[ERROR] MySQL delete_availabilities_for_user: Telegram ID {user_id} - Errore: {e}")

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

def get_all_user_ids():
    with get_connection() as conn:
        cursor = conn.execute("SELECT telegram_id FROM volontari")
        return [row[0] for row in cursor.fetchall()]
