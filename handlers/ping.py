from telegram.ext import ContextTypes
from telegram import Message, Update
from config import ADMIN_CHAT_ID
import asyncio

async def ping_admin(context: ContextTypes.DEFAULT_TYPE):
    # Invia il messaggio
    message: Message = await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text="✅ Il bot è attivo.")
    
    # Aspetta 5 minuti (300 secondi)
    await asyncio.sleep(300)
    
    # Cancella il messaggio
    try:
        await context.bot.delete_message(chat_id=ADMIN_CHAT_ID, message_id=message.message_id)
    except Exception as e:
        print(f"Errore nella cancellazione del messaggio di ping: {e}")


# Risposta al comando /ping
async def ping_ok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_CHAT_ID:
        await update.message.reply_text("✅ Ping OK!")
    else:
        await update.message.reply_text("Non sei autorizzato a usare questo comando.")