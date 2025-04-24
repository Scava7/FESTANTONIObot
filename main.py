from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.request import HTTPXRequest  # <-- Importa il gestore con timeout
from config import BOT_TOKEN
import traceback
import telegram
from db.database import init_db, update_schema
from handlers.start import start
from handlers.receive_db import receive_db
from handlers.ping import ping_admin, ping_ok
from datetime import timedelta
from handlers.unknown import handle_unknown
from telegram.ext import MessageHandler, filters
from handlers.getdb import send_db
from telegram.ext import CommandHandler
from handlers.send_daily_db import send_daily_db
from datetime import time, timezone





#test

def main():

    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    import sys
    sys.stderr = open("error.log", "a")


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


    # Aggiunta handler /start
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getdb", send_db))
    app.add_handler(CommandHandler("ping", ping_ok))
    app.add_handler(MessageHandler(filters.Document.ALL, receive_db))
    app.add_handler(MessageHandler(filters.ALL, handle_unknown))

   
    print("Bot avviato.")
    app.run_polling()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        with open("error.log", "a") as log:
            log.write(traceback.format_exc())

        # Invia il file di log a te (sostituisci il tuo ID)
        ADMIN_ID = 123456789  # <-- METTI IL TUO CHAT ID QUI
        bot = telegram.Bot(token=BOT_TOKEN)
        with open("error.log", "rb") as log_file:
            bot.send_document(chat_id=ADMIN_ID, document=log_file, filename="error.log")
