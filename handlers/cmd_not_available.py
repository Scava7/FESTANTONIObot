from telegram import Update
from telegram.ext import ContextTypes
from db.database_operations import increment_command_count
from constants.constants import COLUMN_VOL

async def not_available_yet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

   # Incrementa il contatore dei comandi /start
    increment_command_count(user.id, COLUMN_VOL.N_CMD_MYSHIFT)

    text = (
        "⚙️ Questo comando non è ancora disponibile.\n\n"
        "Se hai bisogno di aiuto, usa il comando /scrivimi per contattare l'organizzatore."
    )
    await update.message.reply_text(text)