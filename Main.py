from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from db.database import init_db
from handlers.start import start

def main():
    # Inizializza DB
    init_db()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Bot avviato.")
    app.run_polling()

if __name__ == "__main__":
    main()