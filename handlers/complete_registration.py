from telegram import Update
from telegram.ext import ContextTypes
from db.database import save_volunteer
from config import ADMIN_CHAT_ID

async def handle_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_name"):
        return  # Ignora se l'utente non è in fase di registrazione

    try:
        name_parts = update.message.text.strip().split()
        if len(name_parts) != 2:
            await update.message.reply_text("⚠️ Scrivi *solo* nome e cognome, separati da uno spazio (es. `Mario Rossi`).", parse_mode="Markdown")
            return

        name, last_name = name_parts
        user = update.effective_user

        # Salva nel DB
        save_volunteer(user, name=name, last_name=last_name)

        info = (
        f"\U0001F464 Nuovo volontario registrato:\n"
        f"ID: {user.id}\n"
        f"Nome: {name} {last_name}\n"
        f"Username: @{user.username or 'Nessuno'}"
    )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=info)

        # Conferma
        await update.message.reply_text(f"✅ Registrazione completata. Benvenuto {name} {last_name}!")

        # Pulisce lo stato
        context.user_data["awaiting_name"] = False

    except Exception as e:
        await update.message.reply_text("❌ Errore nella registrazione. Riprova.")
        print(f"Errore nella gestione del nome: {e}")


