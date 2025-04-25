from telegram import Update
from telegram.ext import ContextTypes
from handlers.contact_admin import handle_user_message
from handlers.handle_name.complete_registration import handle_name_input
from handlers.unknown import handle_unknown

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_message"):
        await handle_user_message(update, context)
    elif context.user_data.get("awaiting_name"):
        await handle_name_input(update, context)
    else:
        await handle_unknown(update, context)