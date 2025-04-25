from telegram import Update
from telegram.ext import ContextTypes
from db.database_operations import increment_command_count
from constants.constants import COLUMN_VOL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Incrementa il contatore dei comandi /start
    increment_command_count(user.id, COLUMN_VOL.N_CMD_START)

    await update.message.reply_text(
        "👋 Ciao! Benvenuto nel bot di FestAntonio.\n\n"
        "Al momento puoi:\n"
        "• Registrarti come volontario con il comando /registrami\n"
        "• Contattarmi qui se hai dubbi o proposte /scrivimi\n\n"
        "Altre funzionalità verranno aggiunte nei prossimi giorni!"
    )