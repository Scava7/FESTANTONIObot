from telegram import Update
from telegram.ext import ContextTypes
from db.database_operations import increment_unknown_count
from util_functions.utility import delete_later 
import asyncio

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message
    user = update.effective_user

    # Incrementa il contatore dei comandi non riconosciuti
    increment_unknown_count(user.id)

    # Rispondi all'utente
    reply = await user_msg.reply_text(
        "⚠️ Comando non riconosciuto.\n\n"
        "Se sei già registrato, usa /disponibilita per gestire i tuoi turni, oppure /lista_comandi per vedere cosa puoi fare."
    )

    # Avvia la cancellazione dei messaggi in background
    asyncio.create_task(
        delete_later(context, user_msg.chat_id, user_msg.message_id, reply.message_id, delay=10)
    )