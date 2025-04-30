import subprocess
import datetime
import os
from telegram import Update
from telegram.ext import ContextTypes
from config import MYSQL_PASSWORD, ADMIN_CHAT_ID

# === Configurazione ===
MYSQL_USER = "Scava7"
MYSQL_DB = "Scava7$festantonio"
MYSQL_HOST = "Scava7.mysql.pythonanywhere-services.com"
BACKUP_FOLDER = "/home/Scava7/tmp"
AUTHORIZED_USER_IDS = [ADMIN_CHAT_ID]  # Inserisci il tuo telegram_id
MAX_BACKUPS = 5  # Numero massimo di file da mantenere


def cleanup_old_backups(folder: str, pattern: str, keep: int):
    files = sorted(
        [f for f in os.listdir(folder) if f.startswith(pattern)],
        key=lambda f: os.path.getmtime(os.path.join(folder, f))
    )
    while len(files) > keep:
        old = files.pop(0)
        os.remove(os.path.join(folder, old))

async def backup_mysql_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in AUTHORIZED_USER_IDS:
        await update.message.reply_text("Non hai il permesso per eseguire questa azione.")
        return

    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    today = datetime.date.today().strftime("%Y%m%d")
    filename = f"backup_festantonio_{today}.sql"
    filepath = os.path.join(BACKUP_FOLDER, filename)

    # Rimuove backup più vecchi se ci sono più di MAX_BACKUPS
    cleanup_old_backups(BACKUP_FOLDER, "backup_festantonio_", MAX_BACKUPS)

    command = [
        "mysqldump",
        "-u", MYSQL_USER,
        f"-p{MYSQL_PASSWORD}",
        "-h", MYSQL_HOST,
        MYSQL_DB
    ]

    try:
        with open(filepath, "w") as f:
            subprocess.run(command, stdout=f, stderr=subprocess.PIPE, check=True)

        await update.message.reply_document(
            document=open(filepath, "rb"),
            filename=filename,
            caption=f"Backup MySQL {today} completato. I più vecchi sono stati eliminati."
        )
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"Errore durante il backup:\n{e.stderr.decode()}")