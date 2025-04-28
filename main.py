from telegram.request import HTTPXRequest  # <-- Importa il gestore con timeout
import telegram
from telegram.ext import MessageHandler, filters, CommandHandler, ApplicationBuilder, CallbackQueryHandler
from config import ENABLE_TERMINAL_DEBUG

import traceback

from db.database_operations import init_db
from db.database_checks import update_schema

from datetime import time, timezone, timedelta

#Config
from config import BOT_TOKEN, ADMIN_CHAT_ID

#Error logging
from log_error.setup_logging import setup_logging

#handlers
from db.send_daily_db import send_daily_db
from handlers.handle_name.complete_registration import handle_name_input
from handlers.unknown import handle_unknown
from handlers.registering import register_new_volunteer
from handlers.receive_db import receive_db
from handlers.getdb import send_db
from handlers.ping import ping_admin, ping_ok
from handlers.start import start
from handlers.get_commands import lista_comandi
from handlers.availability import handle_availability_response, availability
from handlers.contact_admin import scrivimi
from handlers.texts import handle_text_message
from handlers.cmd_not_available import not_available_yet
from handlers.admin_broadcast import broadcast_availability
from handlers.reply_users import reply
from handlers.text_directly_users import text_user, handle_text_user_callback, handle_text_user_message


def main():

    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Inizializza il logging
    setup_logging()

    # Inizializza il database
    init_db()

    # Aggiorna lo schema se servono nuove colonne
    update_schema()

    # Timeout personalizzati per evitare errori di connessione su PythonAnywhere
    request = HTTPXRequest(connect_timeout=5.0, read_timeout=15.0)

    # Costruzione del bot con timeout personalizzati
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    # Aggiunta job ricorrente ogni 2 ore
    app.job_queue.run_repeating(ping_admin, interval=timedelta(hours=2), first=10)

    # Job giornaliero alle 19:00 ora del server (UTC+0 su PythonAnywhere)
    app.job_queue.run_daily(send_daily_db, time=time(17, 0, tzinfo=timezone.utc))  # 19:00 Italia = 17:00 UTC

    # Vari handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("broadcast", broadcast_availability))
    app.add_handler(CommandHandler("lista_comandi", lista_comandi))
    app.add_handler(CommandHandler("miei_turni", not_available_yet))
    app.add_handler(CommandHandler("tutti_turni", not_available_yet))
    app.add_handler(CommandHandler("registrami", register_new_volunteer))
    app.add_handler(CommandHandler("getdb", send_db))
    app.add_handler(CommandHandler("ping", ping_ok))
    app.add_handler(CommandHandler("disponibilita", availability))
    app.add_handler(CommandHandler("scrivimi", scrivimi))
    app.add_handler(CommandHandler("reply", reply))
    app.add_handler(CommandHandler("text_user", text_user))
    
    # ⚡ METTI QUI SUBITO DOPO I COMMAND:
    app.add_handler(CallbackQueryHandler(handle_availability_response))
    app.add_handler(CallbackQueryHandler(handle_text_user_callback, pattern=r"^textuser\|"))

    # 📦 SOLO DOPO AGGIUNGI I MESSAGE HANDLER
    #app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name_input))
    app.add_handler(MessageHandler(filters.TEXT, handle_text_user_message))
    app.add_handler(MessageHandler(filters.Document.ALL, receive_db))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(MessageHandler(filters.ALL, handle_unknown))

    if ENABLE_TERMINAL_DEBUG:
        print("Bot avviato.")

    app.run_polling()


import asyncio

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        from telegram import Bot

        with open("error.log", "a") as log:
            log.write(traceback.format_exc())

        async def send_error_log():
            bot = Bot(token=BOT_TOKEN)
            try:
                with open("error.log", "rb") as log_file:
                    await bot.send_document(chat_id=ADMIN_CHAT_ID, document=log_file, filename="error.log")
            except Exception as send_error:
                print(f"Errore nell'invio del file log: {send_error}")

        asyncio.run(send_error_log())