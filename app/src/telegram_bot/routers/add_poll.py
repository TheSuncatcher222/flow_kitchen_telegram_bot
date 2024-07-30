from datetime import time

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import (
    StatesGroup,
    State,
)
from aiogram.types import Message

from app.src.crud.sync_crud.poll_sync_crud import poll_sync_crud
from app.src.database.database import (
    RedisKeys,
    sync_session_maker,
)
from app.src.utils.auth import check_if_user_is_admin
from app.src.utils.bot_delete_messages import bot_delete_messages_list
from app.src.utils.chat import (
    get_chat_id_by_title,
    get_chat_all_titles,
)
from app.src.utils.redis_data import redis_delete
from app.src.utils.reply_keyboard import (
    make_row_keyboard,
    KEYBOARD_MAIN_MENU_ADMIN,
    KEYBOARD_YES_NO,
)
from app.src.utils.poll import translate_days_of_week_from_rus_to_eng
from app.src.validators.poll import (
    validate_poll_chat_id,
    validate_poll_days,
    validate_poll_time,
    validate_poll_title,
    validate_poll_topic,
    validate_poll_options,
    validate_poll_yes_no,
)

router: Router = Router()


class PollForm(StatesGroup):
    """Состояния для опроса."""

    title = State()
    topic = State()
    options = State()
    chat_id = State()
    days = State()
    time = State()
    is_allows_anonymous_answers = State()
    is_allows_multiple_answers = State()

    _init_message_id: int


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
    if not check_if_user_is_admin(user_id=message.from_user.id):
        return

    await message.answer(
        text=(
            'Как будет называться для тебя этот опрос в панели управления? '
            'Например, "Мой очень важный опрос на вт/чт"'
        ),
        reply_markup=None,
    )
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
    try:
        validate_poll_title(value=message.text)
    except ValueError as e:
        await message.answer(text=str(e))
        return

    await state.update_data(title=message.text)

    await message.answer(
        text=(
            'Какая будет тема опроса? '
            'Например, "Придешь завтра?"'
        ),
        reply_markup=None,
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
    try:
        validate_poll_topic(value=message.text)
    except ValueError as e:
        await message.answer(text=str(e))
        return

    await state.update_data(topic=message.text)

    await message.answer(
        text=(
            'Укажи варианты ответов, разделяя их запятыми. '
            'Например, "Партнер,Партнерша,Нет"'
        ),
        reply_markup=None,
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
    try:
        validate_poll_options(value=message.text)
    except ValueError as e:
        await message.answer(text=str(e))
        return

    await state.update_data(options=message.text)

    all_chat_titles: list[str] = get_chat_all_titles()
    await message.answer(
        text=(
            'В какой телеграм чат отправлять опрос?'
        ),
        reply_markup=make_row_keyboard(items=all_chat_titles),
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
    try:
        validate_poll_chat_id(value=message.text)
    except ValueError as e:
        all_chat_titles: list[str] = get_chat_all_titles()
        await message.answer(
            text=str(e),
            reply_markup=make_row_keyboard(items=all_chat_titles),
        )
        return

    await state.update_data(chat_id=message.text)
    await message.answer(
        text=(
            'В какие дни недели отправлять? '
            'Укажи варианты ответов, разделяя их запятыми. '
            'Например, "вт,чт"'
        ),
        reply_markup=None,
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
    try:
        validate_poll_days(value=message.text)
    except ValueError as e:
        await message.answer(text=str(e))
        return

    await state.update_data(days=message.text)
    await message.answer(
        text=(
            'В какое время отправлять опрос? '
            'Например, "14:00"'
        ),
        reply_markup=None,
    )
    await state.set_state(state=PollForm.time)
    return


@router.message(
    PollForm.time,
)
async def add_poll_ask_is_allows_anonymous_answers(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает время.
    Спрашивает анонимность ответов.
    """
    try:
        validate_poll_time(value=message.text)
    except ValueError as e:
        await message.answer(text=str(e))
        return

    await state.update_data(time=message.text)
    await message.answer(
        text=(
            'Должны ли ответы быть анонимными? '
            'Например, "Да" или "Нет"'
        ),
        reply_markup=KEYBOARD_YES_NO,
    )
    await state.set_state(state=PollForm.is_allows_anonymous_answers)
    return

@router.message(
    PollForm.is_allows_anonymous_answers,
)
async def add_poll_ask_is_allows_multiple_answers(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает анонимность ответов.
    Спрашивает возможность множественного выбора.
    """
    try:
        validate_poll_yes_no(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_YES_NO,
        )
        return

    await state.update_data(is_allows_anonymous_answers=message.text)
    await message.answer(
        text=(
            'Можно ли выбирать несколько ответов? '
            'Например, "Да" или "Нет"'
        ),
        reply_markup=KEYBOARD_YES_NO,
    )
    await state.set_state(state=PollForm.is_allows_multiple_answers)
    return


@router.message(
    PollForm.is_allows_multiple_answers,
)
async def add_poll_ask_finish(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает возможность множественного выбора.
    Завершает добавление опроса.
    """
    try:
        validate_poll_yes_no(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_YES_NO,
        )
        return

    await state.update_data(is_allows_multiple_answers=message.text)
    poll: dict[str, any] = await state.get_data()

    obj_data: dict[str, any] = {
        # TODO. А если чат изменит имя?.
        'chat_id': get_chat_id_by_title(title=poll['chat_id']),
        'is_allows_anonymous_answers': True if poll['is_allows_anonymous_answers'] == 'Да' else False,
        'is_allows_multiple_answers': True if poll['is_allows_multiple_answers'] == 'Да' else False,
        'topic': poll['topic'],
        'options': [i.capitalize() for i in poll['options'].split(',')],
        'send_days_of_week_list': translate_days_of_week_from_rus_to_eng(poll['days'].split(',')),
        'send_time': time.fromisoformat(poll['time']),
        'title': poll['title'],
        'user_id': message.from_user.id,
    }

    err_occurred: bool = False
    try:
        with sync_session_maker() as session:
            poll_sync_crud.create(
                obj_data=obj_data,
                session=session,
            )
    except Exception as err:
        err_occurred: bool = True
        await message.answer(
            text=str(err),
            reply_markup=KEYBOARD_MAIN_MENU_ADMIN,
        )

    await state.clear()

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

    if not err_occurred:
        await message.answer(
            text=(
                'Опрос добавлен в рассылку.'
                '\n\n'
                f'Название: {poll['title']}\n'
                f'Тема: {poll['topic']}\n'
                f'Ответы: {poll['options']}\n'
                f'Чат: {poll['chat_id']}\n'
                f'Дни: {poll['days']}\n'
                f'Время: {poll['time']}\n'
                f'Анонимные ответы: {poll['is_allows_anonymous_answers']}\n'
                f'Множественные ответы: {poll['is_allows_multiple_answers']}'
            ),
            reply_markup=KEYBOARD_MAIN_MENU_ADMIN,
        )
        redis_delete(key=RedisKeys.POLL_ALL)

    return
