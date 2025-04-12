from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.request import HTTPXRequest  # <-- Importa il gestore con timeout
from config import BOT_TOKEN
from db.database import init_db
from handlers.start import start

#test

def main():
    # Inizializza il database
    init_db()

    # Timeout personalizzati per evitare errori di connessione su PythonAnywhere
    request = HTTPXRequest(connect_timeout=5.0, read_timeout=15.0)

    # Costruzione del bot con timeout personalizzati
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    # Aggiunta handler /start
    app.add_handler(CommandHandler("start", start))

    print("Bot avviato.")
    app.run_polling()

if __name__ == "__main__":
    main()