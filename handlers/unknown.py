from telegram import Update
from telegram.ext import ContextTypes
import asyncio

async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message

    # Rispondi all'utente (opzionale)
    reply = await user_msg.reply_text("⚠️ Comando non riconosciuto. Usa /start per registrarti.")

    # Aspetta qualche secondo
    await asyncio.sleep(10)

    try:
        # Cancella il messaggio dell'utente
        await context.bot.delete_message(chat_id=user_msg.chat_id, message_id=user_msg.message_id)

        # Cancella la risposta del bot
        await context.bot.delete_message(chat_id=reply.chat_id, message_id=reply.message_id)
    except Exception as e:
        print(f"Errore nella cancellazione dei messaggi: {e}")
