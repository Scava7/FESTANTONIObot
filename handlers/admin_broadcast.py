from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_CHAT_ID
from db.database_operations import get_all_user_ids

async def broadcast_availability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Controlla che sia l'amministratore
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Non hai il permesso per eseguire questo comando.")
        return

    # Messaggio da inviare
    message_text = (
        "🚀 È ora possibile registrare le tue disponibilità FESTANTONIO!\n\n"
        "Usa subito il comando /disponibilita per indicarci quando puoi aiutarci.\n\n"
        "Grazie mille per il tuo supporto!"
    )

    # Prendi tutti gli ID degli utenti registrati
    user_ids = get_all_user_ids()

    sent = 0
    failed = 0

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=message_text)
            sent += 1
        except Exception as e:
            print(f"Errore nell'invio a {uid}: {e}")
            failed += 1

    await update.message.reply_text(f"✅ Messaggio inviato a {sent} utenti. ❌ Falliti: {failed}")