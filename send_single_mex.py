# send_message_ext.py

import asyncio
from telegram.ext import Application
from config import BOT_TOKEN

async def main():
    # Inizializza l'app del bot
    app = Application.builder().token(BOT_TOKEN).build()

    # Prendi dati da input
    telegram_id = int(input("Inserisci l'ID Telegram dell'utente: "))
    text = input("Scrivi il messaggio da inviare: ")

    # Manda il messaggio
    await app.bot.send_message(chat_id=telegram_id, text=text)

if __name__ == "__main__":
    asyncio.run(main())