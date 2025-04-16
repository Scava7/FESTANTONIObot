from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_CHAT_ID

import os

DB_PATH = "data/festantonio.db"

async def send_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ Non hai i permessi per usare questo comando.")
        return

    if not os.path.exists(DB_PATH):
        await update.message.reply_text("❌ Database non trovato.")
        return

    await context.bot.send_document(chat_id=update.effective_chat.id, document=open(DB_PATH, "rb"))
