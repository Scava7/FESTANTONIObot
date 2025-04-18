from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.request import HTTPXRequest  # <-- Importa il gestore con timeout
from config import BOT_TOKEN
from db.database import init_db
from handlers.start import start
from handlers.ping import ping_admin, ping_ok
from datetime import timedelta
from handlers.unknown import handle_unknown
from telegram.ext import MessageHandler, filters
from handlers.getdb import send_db
from telegram.ext import CommandHandler




#test

def main():
    # Inizializza il database
    init_db()


    # Timeout personalizzati per evitare errori di connessione su PythonAnywhere
    request = HTTPXRequest(connect_timeout=5.0, read_timeout=15.0)


    # Costruzione del bot con timeout personalizzati
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()


    # Aggiunta job ricorrente ogni 2 ore
    app.job_queue.run_repeating(ping_admin, interval=timedelta(hours=2), first=10)


    # Aggiunta handler /start
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("getdb", send_db))
    app.add_handler(CommandHandler("ping", ping_ok))
    app.add_handler(MessageHandler(filters.ALL, handle_unknown))

   
    print("Bot avviato.")
    app.run_polling()


if __name__ == "__main__":
    main()