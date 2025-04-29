# handlers/promemoria.py

from telegram.ext import Application
from db.database_operations import get_all_user_ids, get_user_availabilities

async def send_reminder_to_inactive_volunteers(application: Application):
    """
    Invia un messaggio a tutti i volontari registrati che non hanno ancora
    inserito disponibilità per l'evento.
    """
    user_ids = get_all_user_ids()

    for user_id in user_ids:
        if not get_user_availabilities(user_id):
            try:
                await application.bot.send_message(
                    chat_id=user_id,
                    text=(
                        "🗓️ Ciao! Ti ricordiamo di segnalare la tua disponibilità per l'evento con il comando /disponibilita.\n"
                        "Ci aiuti molto pianificando in anticipo. Grazie!"
                    )
                )
            except Exception as e:
                print(f"Errore nell'invio del promemoria a {user_id}: {e}")
