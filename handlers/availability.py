from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import date, timedelta
from db.database import save_availability, get_user_availabilities

# Date e fasce orarie
START_DATE = date(2024, 6, 7)
END_DATE = date(2024, 6, 14)
SLOTS = ["17:30–21:00", "20:30–23:30"]

# Handler per i pulsanti cliccati
async def handle_availability_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ Registrato!", show_alert=False)

    data = query.data
    if data.startswith("disp|"):
        _, giorno, fascia = data.split("|")
        user = query.from_user

        # Salva la disponibilità nel database
        save_availability(user.id, giorno, fascia)

        # Recupera tutte le disponibilità dell'utente
        disponibilita = get_user_availabilities(user.id)
        riepilogo = "\n".join([f"{g} – {f}" for g, f in disponibilita])

        # Ricrea tastiera
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

        await query.edit_message_text(
            text=f"✅ Hai selezionato finora:\n{riepilogo}\n\nPuoi aggiungere altri turni cliccando sotto:",
            reply_markup=reply_markup
        )

    elif data == "ignore":
        await query.answer()