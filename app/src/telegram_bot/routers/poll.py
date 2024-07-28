from aiogram import (
    Router,
    F,
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import (
    StatesGroup,
    State,
)
from aiogram.types import Message

from app.src.utils.bot_delete_messages import bot_delete_messages_list
from app.src.utils.reply_keyboard import KEYBOARD_MAIN_MENU_ADMIN

router: Router = Router()

F_YES_NO = ['Да', 'Нет']


class PollForm(StatesGroup):
    """Состояния для опроса."""

    title = State()
    topic = State()
    options = State()
    chat_id = State()
    days = State()
    time = State()
    is_anonymous_answers = State()
    is_allows_multiple_answers = State()

    _init_message_id: int


from logging import Logger


logger = Logger(__name__)


@router.message(
    Command('add_poll'),
)
async def add_pool_ask_title(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Инициализирует форму создания опроса.
    Спрашивает название опроса в панели управления.
    """
    await state.update_data(chat_id=message.chat.id)
    message_reply = await message.answer(
        text=(
            'Как будет называться для тебя этот опрос в панели управления? '
            'Например, "Мой очень важный опрос на вт/чт"'
        ),
    )
    logger.warning(message_reply.message_id)
    await state.set_state(state=PollForm.title)
    await state.update_data(_init_message_id=message.message_id)

    return


@router.message(
    PollForm.title,
)
async def add_pool_ask_topic(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает название опроса в панели управления.
    Спрашивает тему опроса.
    """
    await state.update_data(title=message.text)
    await message.answer(
        text=(
            'Какая будет тема опроса? '
            'Например, "Да или нет"?'
        ),
    )
    await state.set_state(state=PollForm.topic)
    return


@router.message(
    PollForm.topic,
)
async def add_poll_ask_options(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает тему опроса.
    Спрашивает варианты ответов.
    """
    await state.update_data(topic=message.text)
    await message.answer(
        text=(
            'Укажи варианты ответов, разделяя их запятыми. '
            'Например, "Да,Нет"'
        ),
    )
    await state.set_state(state=PollForm.options)
    return


@router.message(
    PollForm.options,
)
async def add_poll_ask_chat_id(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает варианты ответов.
    Спрашивает чат ID.
    """
    await state.update_data(options=message.text)
    await message.answer(
        text=(
            'В какой телеграм чат отправлять опрос?'
        ),
        # TODO. Добавить.
        # reply_markup=make_row_keyboard()
    )
    await state.set_state(state=PollForm.chat_id)
    return


@router.message(
    PollForm.chat_id,
)
async def add_poll_ask_days(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает чат ID.
    Спрашивает в какие дни недели отправлять.
    """
    # TODO. Парсить данные.
    await state.update_data(chat_id=message.text)
    await message.answer(
        text=(
            'В какие дни недели отправлять? '
            'Укажи варианты ответов, разделяя их запятыми. '
            'Например, "вт,чт"'
        ),
    )
    await state.set_state(state=PollForm.days)
    return


@router.message(
    PollForm.days,
)
async def add_poll_ask_time(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает в какие дни недели отправлять.
    Спрашивает время.
    """
    await state.update_data(days=message.text)
    await message.answer(
        text=(
            'В какое время отправлять опрос? '
            'Например, "14:00"'
        ),
    )
    await state.set_state(state=PollForm.time)
    return


@router.message(
    PollForm.time,
)
async def add_poll_ask_is_anonymous_answers(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает время.
    Спрашивает анонимность ответов.
    """
    await state.update_data(time=message.text)
    await message.answer(
        text=(
            'Должны ли ответы быть анонимными? '
            'Например, "Да" или "Нет"'
        ),
    )
    await state.set_state(state=PollForm.is_anonymous_answers)
    return

@router.message(
    PollForm.is_anonymous_answers,
    F.text.in_(F_YES_NO),
)
async def add_poll_ask_is_allows_multiple_answers(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает анонимность ответов.
    Спрашивает возможность множественного выбора.
    """
    await state.update_data(is_anonymous_answers=message.text)
    await message.answer(
        text=(
            'Можно ли выбирать несколько ответов? '
            'Например, "Да" или "Нет"'
        ),
    )
    await state.set_state(state=PollForm.is_allows_multiple_answers)
    return


@router.message(
    PollForm.is_allows_multiple_answers,
    F.text.in_(F_YES_NO),
)
async def add_poll_ask_finish(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает возможность множественного выбора.
    Завершает добавление опроса.
    """
    await state.update_data(is_allows_multiple_answers=message.text)
    poll: dict[str, any] = await state.get_data()
    await state.clear()

    # INFO. Вместе с командой "/add_poll" будет 17 сообщений до этого момента.
    previous_messages: list[int] = list(
        range(
            poll['_init_message_id'],
            message.message_id + 1,
        ),
    )
    await bot_delete_messages_list(
        chat_id=message.chat.id,
        messages_ids=previous_messages,
    )

    await message.answer(
        text=(
            'Опрос добавлен.'
            '\n\n'
            f'Название: {poll['title']}\n'
            f'Тема: {poll['topic']}\n'
            f'Ответы: {poll['options']}\n'
            f'Чат: {poll['chat_id']}\n'
            f'Дни: {poll['days']}\n'
            f'Время: {poll['time']}\n'
            f'Анонимные ответы: {poll['is_anonymous_answers']}\n'
            f'Множественные ответы: {poll['is_allows_multiple_answers']}'
        ),
        reply_markup=KEYBOARD_MAIN_MENU_ADMIN,
    )

    # TODO. Зарегистрировать отправку опросов.

    return
