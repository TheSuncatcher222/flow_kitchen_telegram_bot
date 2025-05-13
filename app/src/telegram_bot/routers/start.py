from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.src.crud.user import user_crud
from app.src.database.database import async_session_maker
from app.src.utils.auth import (
    check_if_user_is_admin,
    check_if_user_is_developer,
)
from app.src.utils.message import delete_messages_list
from app.src.utils.reply_keyboard import get_keyboard_main_menu

if TYPE_CHECKING:
    from app.src.models.user import User

router: Router = Router()


@router.message(CommandStart())
async def command_start(message: Message, from_command_start: bool = True) -> None:
    """
    Обрабатывает команду /start и регистрирует/обновляет пользователя.
    """
    text: str = (
        '👋 Привет! Я Сергей Пилипчак — танцор, преподаватель и создатель онлайн-курсов, '
        'которые помогут тебе прокачать твою пластику, музыкальность и растяжку 💃🕺'
        '\n\n'
        'Хочешь танцевать уверенно, красиво и с кайфом? Начни прямо сейчас — выбери курс и вперёд!'
        '\n\n'
        '⬇️ Выбирай интересующий курс ⬇️'
    )
    if check_if_user_is_developer(user_id_telegram=message.from_user.id):
        text: str = (
            'Root-доступ к панели управления разрешен ✅'
            '\n\n'
            'Сообщение для обычных пользователей будет таким:'
            '\n\n'
            f'{text}'
        )
    elif check_if_user_is_admin(user_id_telegram=message.from_user.id):
        text: str = (
            'Доступ к панели управления разрешен ✅'
            '\n\n'
            'Сообщение для обычных пользователей будет таким:'
            '\n\n'
            f'{text}'
        )

    if from_command_start:
        await delete_messages_list(
            chat_id=message.chat.id,
            messages_ids=[message.message_id],
        )
    answer: Message = await message.answer(
        text=text,
        reply_markup=await get_keyboard_main_menu(user_id_telegram=message.from_user.id),
    )

    async with async_session_maker() as session:
        user: User | None = await user_crud.retrieve_by_id_telegram(
            obj_id_telegram=message.from_user.id,
            session=session,
        )
        if not user:
            user: User = await user_crud.create(
                obj_data={
                    'id_telegram': str(message.from_user.id),
                    'message_main_last_id': answer.message_id,
                    'name_first': message.from_user.first_name,
                    'name_last': message.from_user.last_name,
                    'username': message.from_user.username,
                },
                session=session,
                perform_commit=False,
            )
        else:
            await delete_messages_list(
                chat_id=message.chat.id,
                messages_ids=[user.message_main_last_id],
            )
        await user_crud.update_by_id(
            obj_id=user.id,
            obj_data={
                'datetime_stop': None,
                'is_stopped_bot': False,
                'message_main_last_id': answer.message_id,
                'name_first': message.from_user.first_name,
                'name_last': message.from_user.last_name,
                'username': message.from_user.username,
            },
            session=session,
        )
