from telegram import Update
from telegram.ext import ContextTypes

async def not_available_yet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    text = (
        "⚙️ Questo comando non è ancora disponibile.\n\n"
        "Se hai bisogno di aiuto, usa il comando /scrivimi per contattare l'organizzatore."
    )
    await update.message.reply_text(text)