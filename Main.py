# main.py
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, admin_chat_id


TOKEN = BOT_TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Risposta all'utente
    await update.message.reply_text("Ciao! Sei connesso al bot.")

    # Messaggio privato a te (l'amministratore)
    info = (
        f"👤 Nuovo utente ha avviato il bot:\n"
        f"ID: {user.id}\n"
        f"Nome: {user.first_name} {user.last_name or ''}\n"
        f"Username: @{user.username or 'Nessuno'}"
    )
    await context.bot.send_message(chat_id=admin_chat_id, text=info)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hai detto: {update.message.text}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()






