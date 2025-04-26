from telegram import Update
from telegram.ext import ContextTypes
from db.database_operations import increment_command_count
from constants.constants import COLUMN_VOL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Incrementa il contatore dei comandi /start
    increment_command_count(user.id, COLUMN_VOL.N_CMD_START)

    await update.message.reply_text(
        "🎉 Benvenuto nel bot ufficiale di *FestAntonio*! 🎉\n\n"
        "Qui puoi:\n"
        "👉 /registrami – Unisciti come volontario!\n"
        "👉 /disponibilita – Segnala quando puoi dare una mano\n"
        "👉 /scrivimi – Scrivimi direttamente se hai dubbi o proposte\n\n"
        "🎯 Altre novità in arrivo nei prossimi giorni... resta sintonizzato!"
        , parse_mode="Markdown"
    )