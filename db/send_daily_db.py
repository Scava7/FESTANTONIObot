from telegram.ext import ContextTypes
from config import ADMIN_CHAT_ID
from config import DB_PATH  # Deve contenere il path assoluto o relativo al .db

async def send_daily_db(context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(DB_PATH, "rb") as db_file:
            await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=db_file, filename="festantonio.db")
    except Exception as e:
        print(f"Errore nell'invio del DB: {e}")
