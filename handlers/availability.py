from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import date, timedelta
from db.database_operations import save_availability, get_user_availabilities, delete_availabilities_for_user
from handlers.contact_admin import notify_admin_availability_confirmed

# Date e fasce orarie
START_DATE = date(2025, 6, 7)
END_DATE = date(2025, 6, 14)
SLOTS = ["17:30–21:00", "20:30–23:30"]

# Timeout per conferma disponibilità (secondi)
AVAILABILITY_TIMEOUT = 20 * 60  # 20 minuti

# Dizionario manuale per la traduzione
GIONRI_SETTIMANA = {
    "Monday": "Lunedì",
    "Tuesday": "Martedì",
    "Wednesday": "Mercoledì",
    "Thursday": "Giovedì",
    "Friday": "Venerdì",
    "Saturday": "Sabato",
    "Sunday": "Domenica"
}

MESI_ANNO = {
    "January": "Gennaio",
    "February": "Febbraio",
    "March": "Marzo",
    "April": "Aprile",
    "May": "Maggio",
    "June": "Giugno",
    "July": "Luglio",
    "August": "Agosto",
    "September": "Settembre",
    "October": "Ottobre",
    "November": "Novembre",
    "December": "Dicembre"
}

async def availability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    context.user_data["pending_availability"] = []
    context.user_data["availability_message_id"] = None

    keyboard = generate_availability_keyboard()

    message = await update.message.reply_text(
        "Seleziona i turni in cui sei disponibile.\n\nQuando hai finito, premi CONFERMA oppure ANNULLA.",
        reply_markup=keyboard
    )

    context.user_data["availability_message_id"] = message.message_id

    context.job_queue.run_once(cancel_availability, AVAILABILITY_TIMEOUT, chat_id=update.effective_chat.id, name=str(user.id))


async def handle_availability_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user

    if "pending_availability" not in context.user_data:
        context.user_data["pending_availability"] = []

    pending = context.user_data["pending_availability"]

    if data.startswith("disp|"):
        _, giorno, fascia = data.split("|")
        selection = (giorno, fascia)

        if selection in pending:
            pending.remove(selection)
        else:
            pending.append(selection)

        await update_pending_availability_message(query, context)

    elif data.startswith("day|"):
        _, giorno = data.split("|")
        selection1 = (giorno, "17:30–21:00")
        selection2 = (giorno, "20:30–23:30")

        if selection1 in pending and selection2 in pending:
            pending.remove(selection1)
            pending.remove(selection2)
        else:
            if selection1 not in pending:
                pending.append(selection1)
            if selection2 not in pending:
                pending.append(selection2)

        await update_pending_availability_message(query, context)

    elif data == "conferma":
        await confirm_availability(query, context)

    elif data == "annulla":
        await cancel_availability_manual(query, context)

    elif data == "ignore":
        await query.answer()


def generate_availability_keyboard(selected=None):
    if selected is None:
        selected = []

    keyboard = []
    current = START_DATE
    while current <= END_DATE:
        giorno_str = str(current)

        giorno_eng = current.strftime('%A')
        mese_eng = current.strftime('%B')
        giorno_num = current.strftime('%d')

        giorno_ita = GIONRI_SETTIMANA.get(giorno_eng, giorno_eng)
        mese_ita = MESI_ANNO.get(mese_eng, mese_eng)

        giorno_label_text = f"{giorno_ita} {giorno_num} {mese_ita}"

        all_selected = (
            (giorno_str, "17:30–21:00") in selected and
            (giorno_str, "20:30–23:30") in selected
        )
        giorno_label = f"✅ {giorno_label_text}" if all_selected else f"🗓️ {giorno_label_text}"

        keyboard.append([
            InlineKeyboardButton(giorno_label, callback_data=f"day|{giorno_str}")
        ])

        day_buttons = []
        for slot in SLOTS:
            label = f"✅ {slot}" if (giorno_str, slot) in selected else f"⭕ {slot}"
            day_buttons.append(InlineKeyboardButton(label, callback_data=f"disp|{giorno_str}|{slot}"))
        keyboard.append(day_buttons)

        current += timedelta(days=1)

    keyboard.append([
        InlineKeyboardButton("✅ CONFERMA", callback_data="conferma"),
        InlineKeyboardButton("❌ ANNULLA", callback_data="annulla")
    ])

    return InlineKeyboardMarkup(keyboard)


async def update_pending_availability_message(query, context):
    disponibilita = context.user_data.get("pending_availability", [])

    if disponibilita:
        giorni = {}
        for giorno, fascia in disponibilita:
            if giorno not in giorni:
                giorni[giorno] = []
            giorni[giorno].append(fascia)

        righe = []
        for giorno, fasce in sorted(giorni.items()):
            if len(fasce) == 2:
                righe.append(f"{giorno} – 17:30–23:30")
            else:
                righe.append(f"{giorno} – {fasce[0]}")

        riepilogo = "\n".join(righe)
    else:
        riepilogo = "(nessuna selezione)"

    try:
        await query.edit_message_text(
            text=f"Hai selezionato finora:\n{riepilogo}\n\nPremi CONFERMA oppure ANNULLA.",
            reply_markup=generate_availability_keyboard(selected=disponibilita)
        )
    except Exception as e:
        print(f"Errore aggiornamento messaggio disponibilità: {e}")


async def confirm_availability(query, context):
    user = query.from_user
    pending = context.user_data.get("pending_availability", [])

    if pending:
        delete_availabilities_for_user(user.id)

        for giorno, fascia in pending:
            save_availability(user.id, giorno, fascia, nome_cognome=f"{user.first_name} {user.last_name}")

        await query.edit_message_text("✅ Disponibilità confermata!")
        await notify_admin_availability_confirmed(context.bot, user.id)
    else:
        await query.edit_message_text("⚠️ Nessuna disponibilità selezionata.")

    context.user_data.pop("pending_availability", None)
    context.user_data.pop("availability_message_id", None)


async def cancel_availability(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    await context.bot.send_message(chat_id=chat_id, text="⏳ Tempo scaduto. Registrazione disponibilità annullata.")


async def cancel_availability_manual(query, context):
    await query.edit_message_text("❌ Registrazione disponibilità annullata.")
    context.user_data.pop("pending_availability", None)
    context.user_data.pop("availability_message_id", None)
