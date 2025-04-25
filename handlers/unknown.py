from telegram import Update
from telegram.ext import ContextTypes
from db.database_operations import increment_unknown_count
import asyncio

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message
    user = update.effective_user

    # Incrementa il contatore dei comandi usati
    increment_unknown_count(user.id)

    # Rispondi all'utente (opzionale)
    reply = await user_msg.reply_text("⚠️ Comando non riconosciuto. Usa /start per registrarti.\n\nSe lo hai già fatto, ti informerò io quando saranno disponibili altre informazioni o comandi.")

    # Aspetta qualche secondo
    await asyncio.sleep(10)

    try:
        # Cancella il messaggio dell'utente
        await context.bot.delete_message(chat_id=user_msg.chat_id, message_id=user_msg.message_id)

        # Cancella la risposta del bot
        await context.bot.delete_message(chat_id=reply.chat_id, message_id=reply.message_id)
    except Exception as e:
        print(f"Errore nella cancellazione dei messaggi: {e}")
