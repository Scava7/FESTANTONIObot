from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_CHAT_ID
from db.database import save_volunteer, volunteer_exists, increment_command_count
import asyncio

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Incrementa il contatore dei comandi usati
    increment_command_count(user.id)

    if volunteer_exists(user.id):
        reply = await update.message.reply_text("Utente già registrato. Ti informerò io quando saranno disponibili altre informazioni o comandi.")
        await asyncio.sleep(10)
        try:
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            await context.bot.delete_message(chat_id=reply.chat_id, message_id=reply.message_id)
        except Exception as e:
            print(f"Errore nella cancellazione dei messaggi: {e}")
        return

    # Salva nel DB
    save_volunteer(user)

    # Risposta all'utente
    await update.message.reply_text("Ciao! Sei stato registrato come volontario.")

    # Notifica all’amministratore
    info = (
        f"\U0001F464 Nuovo volontario:\n"
        f"ID: {user.id}\n"
        f"Nome: {user.first_name} {user.last_name or ''}\n"
        f"Username: @{user.username or 'Nessuno'}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=info)
