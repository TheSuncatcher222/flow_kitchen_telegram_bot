from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.src.database.database import RedisKeys
from app.src.utils.auth import check_if_user_is_admin
from app.src.utils.redis_data import redis_delete
from app.src.utils.reply_keyboard import KEYBOARD_MAIN_MENU_ADMIN

router: Router = Router()


@router.message(Command('clear_cache'))
async def command_clear_cache(message: Message) -> None:
    """
    Обрабатывает команду /clear_cache.
    """
    if not check_if_user_is_admin(message.from_user.id):
        return

    for key in (
        RedisKeys.CHAT_ALL_IDS,
        RedisKeys.CHAT_ALL_TITLES,
        RedisKeys.POLL_ALL,
    ):
        redis_delete(key=key)

    await message.answer(
        text='Кеш очищен!',
        reply_markup=KEYBOARD_MAIN_MENU_ADMIN,
    )

    return
