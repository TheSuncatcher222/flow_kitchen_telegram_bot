from aiogram.exceptions import TelegramBadRequest
from aiogram.methods.delete_message import DeleteMessage

from app.src.telegram_bot.bot import bot


async def bot_delete_messages_list(
    chat_id: int,
    messages_ids: list[int],
    raise_exception: bool = False,
) -> None:
    """
    Удаляет указанные сообщения в телеграм чате/группе.
    """
    for message_id in messages_ids:
        try:
            await bot(
                DeleteMessage(
                    chat_id=chat_id,
                    message_id=message_id,
                ),
            )
        except TelegramBadRequest:
            if raise_exception:
                raise
            else:
                continue
    return
