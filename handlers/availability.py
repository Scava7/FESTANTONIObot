from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from datetime import date, timedelta
from db.database import save_availability

# Date e fasce orarie
START_DATE = date(2024, 6, 7)
END_DATE = date(2024, 6, 14)
SLOTS = ["17:30–21:00", "20:30–23:30"]

# Comando per inviare il sondaggio
async def availability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    current = START_DATE
    while current <= END_DATE:
        day_buttons = [
            InlineKeyboardButton(slot, callback_data=f"disp|{current}|{slot}") for slot in SLOTS
        ]
        keyboard.append([InlineKeyboardButton(f"🗓️ {current.strftime('%A %d %B')}", callback_data="ignore")])
        keyboard.append(day_buttons)
        current += timedelta(days=1)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Scegli quando sei disponibile:", reply_markup=reply_markup)

# Handler per i pulsanti cliccati
async def handle_availability_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("disp|"):
        _, giorno, fascia = data.split("|")
        user = query.from_user

        # Salva la disponibilità nel database
        save_availability(user.id, giorno, fascia)

        await query.edit_message_text(f"✅ Hai scelto: {giorno} – {fascia}")
    elif data == "ignore":
        await query.answer()

# Per aggiungerli nel main.py:
# app.add_handler(CommandHandler("disponibilita", availability))
# app.add_handler(CallbackQueryHandler(handle_availability_response))
