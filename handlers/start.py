from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_CHAT_ID
from db.database import save_volunteer

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Salva nel DB
    save_volunteer(user)

    # Risposta all'utente
    await update.message.reply_text("Ciao! Sei stato registrato come volontario.")

    # Notifica all’amministratore
    info = (
        f"👤 Nuovo volontario:\n"
        f"ID: {user.id}\n"
        f"Nome: {user.first_name} {user.last_name or ''}\n"
        f"Username: @{user.username or 'Nessuno'}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=info)