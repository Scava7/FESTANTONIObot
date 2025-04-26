from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import date, timedelta
from db.database_operations import save_availability, get_user_availabilities, delete_availabilities_for_user
from handlers.contact_admin import notify_admin_availability_confirmed

# Date e fasce orarie
START_DATE = date(2024, 6, 7)
END_DATE = date(2024, 6, 14)
SLOTS = ["17:30–21:00", "20:30–23:30"]

# Timeout per conferma disponibilità (secondi)
AVAILABILITY_TIMEOUT = 20 * 60  # 20 minuti

async def availability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Inizializza dati temporanei
    context.user_data["pending_availability"] = []
    context.user_data["availability_message_id"] = None

    # Costruisci tastiera
    keyboard = generate_availability_keyboard()

    # Invia il messaggio
    message = await update.message.reply_text(
        "Seleziona i turni in cui sei disponibile.\n\nQuando hai finito, premi CONFERMA oppure ANNULLA.",
        reply_markup=keyboard
    )

    # Salva ID del messaggio
    context.user_data["availability_message_id"] = message.message_id

    # Imposta un timer automatico per l'annullamento
    context.job_queue.run_once(cancel_availability, AVAILABILITY_TIMEOUT, chat_id=update.effective_chat.id, name=str(user.id))


async def handle_availability_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user

    if data.startswith("disp|"):
        _, giorno, fascia = data.split("|")

        if "pending_availability" not in context.user_data:
            context.user_data["pending_availability"] = []

        selection = (giorno, fascia)

        # Se già selezionato, lo togliamo (toggle)
        if selection in context.user_data["pending_availability"]:
            context.user_data["pending_availability"].remove(selection)
        else:
            context.user_data["pending_availability"].append(selection)

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
        day_buttons = []
        for slot in SLOTS:
            giorno_str = str(current)
            label = f"✅ {slot}" if (giorno_str, slot) in selected else f"⭕ {slot}"
            day_buttons.append(InlineKeyboardButton(label, callback_data=f"disp|{giorno_str}|{slot}"))

        keyboard.append([InlineKeyboardButton(f"🗓️ {current.strftime('%A %d %B')}", callback_data="ignore")])
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
        riepilogo = "\n".join([f"{g} – {f}" for g, f in disponibilita])
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
        # Elimina vecchie disponibilità
        delete_availabilities_for_user(user.id)

        # Salva le nuove
        for giorno, fascia in pending:
            save_availability(user.id, giorno, fascia)

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