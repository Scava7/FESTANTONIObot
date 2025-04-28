# handlers/reply_user.py

from telegram import Update
from telegram.ext import ContextTypes
from db.database_operations import volunteer_exists
from config import ADMIN_CHAT_ID

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Permette all'amministratore di rispondere a un utente tramite il comando /reply."""
    user = update.effective_user

    # Verifica che chi usa il comando sia l'amministratore
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Questo comando è riservato all'amministratore.")
        return

    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Uso corretto: /reply_<user_id> messaggio")
        return

    try:
        full_command = update.message.text
        parts = full_command.split(' ', 1)
        if not parts or len(parts) < 2:
            await update.message.reply_text("Uso corretto: /reply_<user_id> messaggio")
            return

        cmd, text_to_send = parts
        user_id_part = cmd.replace("/reply_", "")
        target_user_id = int(user_id_part)

        if not volunteer_exists(target_user_id):
            await update.message.reply_text("⛔ Utente non trovato.")
            return

        await context.bot.send_message(chat_id=target_user_id, text=text_to_send)
        await update.message.reply_text(f"✅ Messaggio inviato a {target_user_id}.")

    except Exception as e:
        await update.message.reply_text(f"❌ Errore nell'invio: {e}")
