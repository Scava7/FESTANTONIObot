# handlers/handle_text_user_message.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db.database_operations import get_all_user_ids, get_user_info
from config import ADMIN_CHAT_ID


async def handle_text_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Invia il messaggio all'utente selezionato tramite /text_user."""
    if "text_user_target" not in context.user_data:
        return  # Non c'è nessun utente selezionato

    user_id = context.user_data.pop("text_user_target")
    testo = update.message.text

    try:
        await context.bot.send_message(chat_id=user_id, text=testo)
        await update.message.reply_text("✅ Messaggio inviato.")
    except Exception as e:
        await update.message.reply_text(f"❌ Errore: {e}")

async def text_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra la lista utenti per scegliere a chi inviare un messaggio."""
    user = update.effective_user

    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Questo comando è riservato all'amministratore.")
        return

    keyboard = []
    for user_id in get_all_user_ids():
        info = get_user_info(user_id)
        if info.get("name") and info.get("last_name"):
            label = f"{info['name']} {info['last_name']}"
        else:
            label = f"ID {user_id}"

        keyboard.append([
            InlineKeyboardButton(label, callback_data=f"textuser|{user_id}")
        ])

    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📋 Seleziona l'utente a cui vuoi scrivere:",
        reply_markup=markup
    )

async def handle_text_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce il click sul nome utente e attiva la richiesta del testo."""
    query = update.callback_query
    data = query.data

    if not data.startswith("textuser|"):
        return

    _, user_id = data.split("|")
    context.user_data["text_user_target"] = int(user_id)

    await query.message.reply_text(
        "✏️ Scrivi il messaggio che vuoi inviare:"
    )

    await query.answer()