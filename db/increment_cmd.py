from db.database_operations import get_connection
from constants.constants import COLUMN_VOL

def increment_command_count(user_id, column):
    with get_connection() as conn:
        conn.execute(f"""
            UPDATE volontari
            SET {column} = {column} + 1
            WHERE telegram_id = ?
        """, (user_id,))
        conn.commit()


def increment_unknown_count(user_id):
    increment_command_count(user_id, COLUMN_VOL.UNKNOWN)