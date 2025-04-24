from telegram import Update
from telegram.ext import ContextTypes
from db.database import increment_command_count
from constants import COLUMN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Incrementa il contatore dei comandi /start
    increment_command_count(user.id, COLUMN.N_CMD_START)

    await update.message.reply_text(
        "👋 Ciao! Benvenuto nel bot di FestAntonio.\n\n"
        "Al momento puoi:\n"
        "• Registrarti come volontario con il comando /registrami\n"
        "• Contattarmi qui se hai dubbi o proposte\n\n"
        "Altre funzionalità verranno aggiunte nei prossimi giorni!"
    )