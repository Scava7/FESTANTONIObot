from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from datetime import date, timedelta
from db.database_operations import (
    save_availability, 
    get_user_availabilities, 
    delete_availabilities_for_user, 
    get_user_info, 
    increment_command_count
)
from handlers.contact_admin import notify_admin_availability_confirmed
from constants.constants import COLUMN_VOL

# Date e fasce orarie disponibili
START_DATE = date(2025, 6, 7)
END_DATE = date(2025, 6, 14)
SLOTS = ["17:30–21:00", "20:30–23:30"]

# Timeout dopo il quale la selezione viene annullata automaticamente (in secondi)
AVAILABILITY_TIMEOUT = 20 * 60  # 20 minuti

# Traduzione giorni della settimana dall'inglese all'italiano
GIORNI_SETTIMANA = {
    "Monday": "Lunedì",
    "Tuesday": "Martedì",
    "Wednesday": "Mercoledì",
    "Thursday": "Giovedì",
    "Friday": "Venerdì",
    "Saturday": "Sabato",
    "Sunday": "Domenica"
}

# Traduzione mesi dall'inglese all'italiano
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

# ==============================
# Comandi principali
# ==============================

async def availability(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce l'inizio della selezione disponibilità."""
    user = update.effective_user

    # Incrementa il contatore del comando
    increment_command_count(user.id, COLUMN_VOL.N_CMD_DISP)

    # Recupera eventuali disponibilità già salvate
    disponibilita_salvate = get_user_availabilities(user.id)
    context.user_data["pending_availability"] = disponibilita_salvate.copy()

    # Crea la tastiera con i pulsanti
    keyboard = generate_availability_keyboard(selected=disponibilita_salvate)

    # Costruisce il riepilogo visivo delle disponibilità
    riepilogo = build_availability_summary(disponibilita_salvate)

    # Manda il messaggio iniziale con tastiera e riepilogo
    message = await update.message.reply_text(
        text=f"<b>Hai selezionato finora:</b>\n{riepilogo}\n\nPremi <b>CONFERMA</b> oppure <b>ANNULLA</b>.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML 
    )

    # Salva l'ID del messaggio per modifiche future
    context.user_data["availability_message_id"] = message.message_id

    # Avvia il job di timeout
    context.job_queue.run_once(cancel_availability, AVAILABILITY_TIMEOUT, chat_id=update.effective_chat.id, name=str(user.id))


async def handle_availability_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i click dell'utente sui pulsanti di disponibilità."""
    query = update.callback_query
    data = query.data
    user = query.from_user

    # Recupera o inizializza la lista delle selezioni pendenti
    if "pending_availability" not in context.user_data:
        context.user_data["pending_availability"] = []

    pending = context.user_data["pending_availability"]

    # Gestisce il click su una singola fascia oraria
    if data.startswith("disp|"):
        _, giorno, fascia = data.split("|")
        selection = (giorno, fascia)

        if selection in pending:
            pending.remove(selection)
        else:
            pending.append(selection)

        await update_pending_availability_message(query, context)

    # Gestisce il click sull'intero giorno (seleziona o deseleziona entrambe le fasce)
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

    # Conferma della disponibilità
    elif data == "conferma":
        await confirm_availability(query, context)

    # Annulla la registrazione
    elif data == "annulla":
        await cancel_availability_manual(query, context)

    # Ignora altri eventi
    elif data == "ignore":
        await query.answer()


def generate_availability_keyboard(selected=None):
    """Crea la tastiera con i pulsanti di disponibilità."""
    if selected is None:
        selected = []

    keyboard = []
    current = START_DATE
    while current <= END_DATE:
        giorno_str = str(current)

        # Traduzioni in italiano di giorno e mese
        giorno_eng = current.strftime('%A')
        mese_eng = current.strftime('%B')
        giorno_num = current.strftime('%d')

        giorno_ita = GIORNI_SETTIMANA.get(giorno_eng, giorno_eng)
        mese_ita = MESI_ANNO.get(mese_eng, mese_eng)

        giorno_label_text = f"{giorno_ita} {giorno_num} {mese_ita}"

        # Etichetta diversa se entrambe le fasce sono selezionate
        all_selected = (
            (giorno_str, "17:30–21:00") in selected and
            (giorno_str, "20:30–23:30") in selected
        )
        giorno_label = f"✅ {giorno_label_text}" if all_selected else f"🗓️ {giorno_label_text}"

        keyboard.append([
            InlineKeyboardButton(giorno_label, callback_data=f"day|{giorno_str}")
        ])

        # Pulsanti per ogni fascia oraria
        day_buttons = []
        for slot in SLOTS:
            label = f"✅ {slot}" if (giorno_str, slot) in selected else f"⭕ {slot}"
            day_buttons.append(InlineKeyboardButton(label, callback_data=f"disp|{giorno_str}|{slot}"))
        keyboard.append(day_buttons)

        current += timedelta(days=1)

    # Pulsanti finali di conferma e annulla
    keyboard.append([
        InlineKeyboardButton("✅ CONFERMA", callback_data="conferma"),
        InlineKeyboardButton("❌ ANNULLA", callback_data="annulla")
    ])

    return InlineKeyboardMarkup(keyboard)


async def update_pending_availability_message(query, context):
    """Aggiorna il messaggio con il riepilogo dopo un click."""
    disponibilita = context.user_data.get("pending_availability", [])
    riepilogo = build_availability_summary(disponibilita)

    try:
        await query.edit_message_text(
            text=f"<b>Hai selezionato finora:</b>\n{riepilogo}\n\nPremi <b>CONFERMA</b> oppure <b>ANNULLA</b>.",
            reply_markup=generate_availability_keyboard(selected=disponibilita),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(f"Errore aggiornamento messaggio disponibilità: {e}")


async def confirm_availability(query, context):
    """Conferma la disponibilità scelta e salva nel database."""
    user = query.from_user
    pending = context.user_data.get("pending_availability", [])

    # Annulla il timeout
    cancel_timeout_job(context, user.id)

    # Cancella il messaggio dei pulsanti
    availability_message_id = context.user_data.get("availability_message_id")
    if availability_message_id:
        try:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=availability_message_id)
        except Exception as e:
            print(f"Errore cancellazione messaggio conferma: {e}")

    if pending:
        delete_availabilities_for_user(user.id)

        # Recupera nome e cognome
        user_info = get_user_info(user.id)
        nome_cognome = None
        if user_info.get("name") and user_info.get("last_name"):
            nome_cognome = f"{user_info['name']} {user_info['last_name']}"

        # Salva ogni disponibilità
        for giorno, fascia in pending:
            save_availability(user.id, giorno, fascia, nome_cognome=nome_cognome)

        await query.answer("✅ Disponibilità confermata!", show_alert=False)

        riepilogo = build_availability_summary(pending)

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗓️ Modifica disponibilità", switch_inline_query_current_chat="/disponibilita")]
        ])

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=(f"✅ <b>Disponibilità confermata!</b>\n\n"
                  f"<b>Le tue disponibilità sono:</b>\n{riepilogo}\n\n"
                  f"🗓️ Se vuoi modificarle, premi il pulsante qui sotto oppure usa <b>/disponibilita</b>!"),
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

        await notify_admin_availability_confirmed(context.bot, user.id)
    else:
        await query.answer("⚠️ Nessuna disponibilità selezionata.", show_alert=False)

    # Pulisce lo stato
    context.user_data.pop("pending_availability", None)
    context.user_data.pop("availability_message_id", None)


async def cancel_availability_manual(query, context):
    """Annulla manualmente la registrazione della disponibilità."""
    availability_message_id = context.user_data.get("availability_message_id")
    if availability_message_id:
        try:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=availability_message_id)
        except Exception as e:
            print(f"Errore cancellazione messaggio annulla: {e}")

    # Annulla il timeout
    cancel_timeout_job(context, query.from_user.id)
    
    await query.answer("❌ Registrazione disponibilità annullata.", show_alert=False)
    context.user_data.pop("pending_availability", None)
    context.user_data.pop("availability_message_id", None)


async def cancel_availability(context: ContextTypes.DEFAULT_TYPE):
    """Gestisce il timeout automatico di inattività."""
    chat_id = context.job.chat_id

    availability_message_id = context.chat_data.get("availability_message_id")
    if availability_message_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=availability_message_id)
        except Exception as e:
            print(f"Errore cancellazione messaggio timeout: {e}")

    await context.bot.send_message(chat_id=chat_id, text="⏳ Tempo scaduto. Registrazione disponibilità annullata.")


def build_availability_summary(availabilities):
    """Costruisce il riepilogo delle disponibilità in formato testuale."""
    if availabilities:
        giorni = {}
        for giorno, fascia in availabilities:
            if giorno not in giorni:
                giorni[giorno] = []
            giorni[giorno].append(fascia)

        righe = []
        for giorno, fasce in sorted(giorni.items()):
            giorno_data = date.fromisoformat(giorno)
            giorno_eng = giorno_data.strftime('%A')
            mese_eng = giorno_data.strftime('%B')
            giorno_num = giorno_data.strftime('%d')

            giorno_ita = GIORNI_SETTIMANA.get(giorno_eng, giorno_eng)
            mese_ita = MESI_ANNO.get(mese_eng, mese_eng)

            giorno_label = f"{giorno_ita} {giorno_num} {mese_ita}"

            if len(fasce) == 2:
                righe.append(f"{giorno_label} – 17:30–23:30")
            else:
                righe.append(f"{giorno_label} – {fasce[0]}")

        return "\n".join(righe)
    else:
        return "(nessuna selezione)"


def cancel_timeout_job(context, user_id):
    """Cancella eventuali job di timeout ancora attivi per l'utente."""
    current_jobs = context.job_queue.get_jobs_by_name(str(user_id))
    for job in current_jobs:
        job.schedule_removal()
