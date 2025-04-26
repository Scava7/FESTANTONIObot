from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_CHAT_ID
from db.database_operations import volunteer_exists, increment_command_count
from util_functions.utility import delete_later
from constants.constants import COLUMN_VOL
import asyncio

async def register_new_volunteer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Incrementa il contatore dei comandi /registrami
    increment_command_count(user.id, COLUMN_VOL.N_CMD_REGISTR)

    if volunteer_exists(user.id):

        text = (
        f"✅ Risulti già registrato!\n"
        f"Puoi:\n"
        f"• 🗓️ Segnalare la tua disponibilità con /disponibilita\n"
        f"• ✉️ Contattare l'organizzatore con /scrivimi\n"
        f"• 📋 Vedere tutti i comandi con /lista_comandi\n"
        f"Se hai bisogno di aiuto, non esitare a scrivermi!"
    )
            
        reply = await update.message.reply_text(text)

        # Avvia la cancellazione come task separato
        asyncio.create_task(
            delete_later(context, update.message.chat_id, update.message.message_id, reply.message_id, delay=20)
        )
        return

    # Stato di attesa per nome e cognome
    context.user_data["awaiting_name"] = True
    await update.message.reply_text(
        "Per favore, inviami il tuo *nome e cognome* in un unico messaggio.",
        parse_mode="Markdown"
    )

    # Timeout di 3 minuti per annullare la registrazione
    asyncio.create_task(clear_flag_after_delay(context))


async def clear_flag_after_delay(context):
    await asyncio.sleep(180)
    if context.user_data.get("awaiting_name"):
        context.user_data["awaiting_name"] = False
        await context.bot.send_message(chat_id=context._chat_id, text="⏳ Tempo scaduto. Riprova a registrarti con /registrami.")