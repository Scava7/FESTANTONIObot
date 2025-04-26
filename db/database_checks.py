from db.database_operations import get_connection
from constants.constants import COLUMN_VOL, COLUMN_DISP


def safe_add_column(table, column_name, column_def):
    with get_connection() as conn:
        cursor = conn.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if column_name not in columns:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_def}")
            conn.commit()


def update_volontari_table():
    with get_connection() as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS volontari (
                {COLUMN_VOL.TELEGRAM_ID} INTEGER PRIMARY KEY
            )
        """)
        conn.commit()

    safe_add_column("volontari", COLUMN_VOL.N_CMD_START, "INTEGER DEFAULT 0")
    safe_add_column("volontari", COLUMN_VOL.N_CMD_REGISTR, "INTEGER DEFAULT 0")
    safe_add_column("volontari", COLUMN_VOL.UNKNOWN, "INTEGER DEFAULT 0")
    safe_add_column("volontari", COLUMN_VOL.NAME, "TEXT")
    safe_add_column("volontari", COLUMN_VOL.LAST_NAME, "TEXT")
    safe_add_column("volontari", COLUMN_VOL.USERNAME, "TEXT")


def update_disponibilita_table():
    with get_connection() as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS disponibilita (
                {COLUMN_DISP.DISP_ID} INTEGER PRIMARY KEY AUTOINCREMENT
            )
        """)
        conn.commit()

    safe_add_column("disponibilita", COLUMN_DISP.TELEGRAM_ID, "INTEGER NOT NULL")
    safe_add_column("disponibilita", COLUMN_DISP.DISP_GIORNO, "TEXT")
    safe_add_column("disponibilita", COLUMN_DISP.DISP_FASCIA, "TEXT")
    safe_add_column("disponibilita", COLUMN_DISP.DISP_NOMECOGNOME, "TEXT")


def update_schema():
    update_volontari_table()
    update_disponibilita_table()