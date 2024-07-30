from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
)

from app.src.utils.auth import check_if_user_is_admin
from app.src.utils.reply_keyboard import KEYBOARD_MAIN_MENU_ADMIN

router: Router = Router()


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    """
    Обрабатывает команду /start.
    """
    if not check_if_user_is_admin(message.from_user.id):
        reply_markup: None = None
    else:
        reply_markup: ReplyKeyboardMarkup = KEYBOARD_MAIN_MENU_ADMIN

    await message.answer(
        text=(
            'Привет! Хочешь научиться танцевать? '
            'Тогда ты по адресу! https://vk.com/flowkitchen'
        ),
        reply_markup=reply_markup,
    )

    return
