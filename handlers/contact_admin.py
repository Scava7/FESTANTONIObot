from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_CHAT_ID
from db.database import get_user_info
from db.database import increment_command_count
from constants.constants import COLUMN


# Comando /scrivimi
async def scrivimi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Incrementa il contatore dei comandi /scrivimi
    increment_command_count(user.id, COLUMN.N_CMD_TEXTME)

    context.user_data["awaiting_message"] = True
    await update.message.reply_text("✉️ Scrivimi il messaggio che vuoi mandare all'organizzatore.")


# Gestore dei messaggi in attesa
async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.user_data.get("awaiting_message"):
        return

    user = update.effective_user
    message = update.message.text

    # Recupera info volontario se disponibili
    user_info = get_user_info(user.id)
    nome = user_info.get("name", user.first_name or "")
    cognome = user_info.get("last_name", user.last_name or "")
    username = user.username or "Nessuno"

    text = (
        f"📩 Nuovo messaggio da un volontario:\n"
        f"Nome: {nome} {cognome}\n"
        f"ID: {user.id}\n"
        f"Username: @{username}\n"
        f"\n"
        f"Messaggio:\n{message}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
    await update.message.reply_text("✅ Messaggio inviato con successo. Grazie!")
    context.user_data["awaiting_message"] = False
