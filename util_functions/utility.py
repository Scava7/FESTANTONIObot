import asyncio

async def delete_later(context, chat_id, user_message_id, reply_message_id, delay=10):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=user_message_id)
        await context.bot.delete_message(chat_id=chat_id, message_id=reply_message_id)
    except Exception as e:
        print(f"Errore nella cancellazione dei messaggi: {e}")