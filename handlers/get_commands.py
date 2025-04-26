from config import ADMIN_CHAT_ID
from telegram import Update
from telegram.ext import ContextTypes
from db.database_operations import increment_command_count
from constants.constants import COLUMN_VOL


async def lista_comandi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Incrementa il contatore dei comandi /registrami
    increment_command_count(user.id, COLUMN_VOL.N_CMD_CMDLIST)

    base_commands = (
        "Benvenuto!\n\n"
        "Ecco cosa puoi fare:\n"
        "🎤 /registrami – Registrati come volontario\n"
        "✅ /disponibilita – Indica quando puoi aiutare\n"
        "📩 /scrivimi – Invia un messaggio agli organizzatori\n"
        "👤 /miei_turni – Richiedi la lista dei tuoi turni\n"
        "🌈 /tutti_turni – Richiedi la lista di tutti i turni di uno specifico team\n"
    )

    admin_commands = (
        "\n👑 Comandi Admin:\n"
        "⚙️ /getdb – Scarica il database\n"
        "⚙️ /ping – Verifica se il bot è attivo\n"
        "⚙️ /broadcast – Manda messaggio a tutti\n"
    )

    if user.id == ADMIN_CHAT_ID:
        await update.message.reply_text(base_commands + admin_commands)
    else:
        await update.message.reply_text(base_commands)