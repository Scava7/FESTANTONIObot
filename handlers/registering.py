from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_CHAT_ID
from db.database import volunteer_exists, increment_command_count
from constants import COLUMN
import asyncio

async def register_new_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Incrementa il contatore dei comandi /registrami
    increment_command_count(user.id, COLUMN.N_CMD_REGISTR)

    if volunteer_exists(user.id):
        reply = await update.message.reply_text("Utente già registrato. Ti informerò io quando saranno disponibili altre informazioni o comandi.")
        await asyncio.sleep(10)
        try:
            await context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            await context.bot.delete_message(chat_id=reply.chat_id, message_id=reply.message_id)
        except Exception as e:
            print(f"Errore nella cancellazione dei messaggi: {e}")
        return

    # Stato di attesa per nome e cognome
    context.user_data["awaiting_name"] = True
    await update.message.reply_text("Per favore, inviami il tuo *nome e cognome* in un unico messaggio.", parse_mode="Markdown")

    # Timeout di 3 minuti per annullare la registrazione
    async def clear_flag_after_delay():
        await asyncio.sleep(180)
        if context.user_data.get("awaiting_name"):
            context.user_data["awaiting_name"] = False
            await update.message.reply_text("⏳ Tempo scaduto. Riprova a registrarti con /registrami.")

    # Lancia la funzione di timeout
    asyncio.create_task(clear_flag_after_delay())
