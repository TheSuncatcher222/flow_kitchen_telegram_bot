from asyncio import sleep as async_sleep
from aiogram import (
    Router,
    F,
)
from aiogram.types import Message

from app.src.utils.auth import IsDeveloper
from app.src.utils.message import delete_messages_list
from app.src.utils.redis_app import redis_flushall
from app.src.utils.reply_keyboard import RoutersCommands

router: Router = Router()


@router.message(
    IsDeveloper(),
    F.text == RoutersCommands.REDIS_CLEAR,
)
async def command_redis_clear(message: Message) -> None:
    """
    Обрабатывает команду "Очистить Redis".
    """
    redis_flushall()
    await message.answer(text='Redis очищен!')
    await async_sleep(0.5)
    await delete_messages_list(
        chat_id=message.chat.id,
        messages_ids=list(range(message.message_id, message.message_id + 2)),
    )
