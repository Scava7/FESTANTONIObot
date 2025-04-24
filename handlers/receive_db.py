from telegram import Update, Document
from telegram.ext import ContextTypes
import os
import shutil
from datetime import datetime
from config import ADMIN_CHAT_ID, DB_PATH

# Percorso cartella del DB
DB_DIR = os.path.dirname(DB_PATH)
BACKUP_DIR = os.path.join(DB_DIR, "backup")
os.makedirs(BACKUP_DIR, exist_ok=True)

async def receive_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Controllo ID mittente
    if update.effective_user.id != ADMIN_CHAT_ID:
        await message.reply_text("Non sei autorizzato.")
        return

    # Controllo che ci sia un documento
    if not message.document:
        await message.reply_text("Devi inviare un file .db.")
        return

    document: Document = message.document

    # Controllo estensione e nome
    if not document.file_name.endswith(".db"):
        await message.reply_text("Il file deve avere estensione .db.")
        return

    # Scarica il nuovo file
    new_db_path = os.path.join(DB_DIR, "new_uploaded.db")
    file = await context.bot.get_file(document.file_id)
    await file.download_to_drive(new_db_path)

    # Backup del DB attuale
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"festantonio_{timestamp}.db")
    if os.path.exists(DB_PATH):
        shutil.move(DB_PATH, backup_path)

    # Sostituisce con il nuovo DB
    shutil.move(new_db_path, DB_PATH)

    await message.reply_text(f"✅ Database aggiornato. Backup salvato come:\n{os.path.basename(backup_path)}")