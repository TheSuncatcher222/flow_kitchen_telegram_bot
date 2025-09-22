from asyncio import sleep as asyncio_sleep
from datetime import time
from typing import TYPE_CHECKING

from aiogram import (
    Router,
    F,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import (
    StatesGroup,
    State,
)
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)

from app.src.crud.poll import poll_crud
from app.src.database.database import (
    RedisKeys,
    async_session_maker,
)
from app.src.telegram_bot.routers.start import command_start
from app.src.utils.auth import IsAdmin
from app.src.utils.message import delete_messages_list
from app.src.utils.chat import (
    get_chat_id_by_title,
    get_chat_all_titles,
)
from app.src.utils.poll import schedule_poll_sending
from app.src.utils.redis_app import redis_delete
from app.src.utils.reply_keyboard import (
    RoutersCommands,
    make_row_keyboard,
    KEYBOARD_CANCEL,
    KEYBOARD_YES_NO_CANCEL,
)
from app.src.utils.translation import translate_days_of_week_from_rus_to_eng
from app.src.validators.poll import (
    validate_poll_chat_id,
    validate_poll_days,
    validate_poll_time,
    validate_poll_title,
    validate_poll_topic,
    validate_poll_options,
    validate_poll_yes_no,
)

if TYPE_CHECKING:
    from app.src.models.poll import Poll

router: Router = Router()


class PollForm(StatesGroup):
    """
    Состояния для команды "/poll_add".
    """

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
    IsAdmin(),
    F.text == RoutersCommands.POLL_ADD,
)
async def add_poll_ask_title(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Инициализирует форму создания опроса.
    Спрашивает название опроса в панели управления.
    """
    await state.update_data(_init_message_id=message.message_id)
    await state.set_state(state=PollForm.title)

    if not await get_chat_all_titles():
        await message.answer(text='Бот не добавлен ни в один Telegram-чат.')
        await asyncio_sleep(2)
        await __cancel(message=message, state=state)
    else:
        await message.answer(
            text='Как будет называться этот опрос в панели управления? Например, "Хип-Хоп (ср/сб)"',
            reply_markup=KEYBOARD_CANCEL,
        )


@router.message(PollForm.title)
async def add_poll_ask_topic(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает название опроса в панели управления.
    Спрашивает тему опроса.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        validate_poll_title(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    await state.update_data(title=message.text)
    await state.set_state(state=PollForm.topic)

    await message.answer(
        text='Какая будет тема опроса? Например, "Придешь завтра?"',
        reply_markup=KEYBOARD_CANCEL,
    )


@router.message(PollForm.topic)
async def add_poll_ask_options(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает тему опроса.
    Спрашивает варианты ответов.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        validate_poll_topic(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    await state.update_data(topic=message.text)
    await state.set_state(state=PollForm.options)

    await message.answer(
        text='Укажи варианты ответов, разделяя их запятыми. Например, "Партнер,Партнерша,Нет"',
        reply_markup=KEYBOARD_CANCEL,
    )



@router.message(PollForm.options)
async def add_poll_ask_chat_id(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает варианты ответов.
    Спрашивает чат ID.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        validate_poll_options(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    await state.update_data(options=message.text)
    await state.set_state(state=PollForm.chat_id)

    CHUNK_SIZE: int = 2
    titles: list[str] = await get_chat_all_titles()
    rows: list[list[str]] = list(
        (titles[i : i + CHUNK_SIZE] for i in range(0, len(titles), CHUNK_SIZE))
    )
    await message.answer(
        text=('В какой телеграм чат отправлять опрос?'),
        reply_markup=make_row_keyboard(rows=rows),
    )


@router.message(PollForm.chat_id)
async def add_poll_ask_days(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает чат ID.
    Спрашивает в какие дни недели отправлять.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        await validate_poll_chat_id(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=make_row_keyboard(rows=(await get_chat_all_titles(),)),
        )
        return

    await state.update_data(chat_id=message.text)
    await state.set_state(state=PollForm.days)

    await message.answer(
        text=(
            'В какие дни недели отправлять? '
            'Укажи варианты ответов, разделяя их запятыми. '
            'Например, "вт,чт"'
        ),
        reply_markup=KEYBOARD_CANCEL,
    )


@router.message(PollForm.days)
async def add_poll_ask_time(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает в какие дни недели отправлять.
    Спрашивает время.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        validate_poll_days(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    await state.update_data(days=message.text)
    await state.set_state(state=PollForm.time)

    await message.answer(
        text='В какое время отправлять опрос? Например, "14:00"',
        reply_markup=KEYBOARD_CANCEL,
    )


@router.message(PollForm.time)
async def add_poll_ask_is_allows_anonymous_answers(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает время.
    Спрашивает анонимность ответов.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        validate_poll_time(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    await state.update_data(time=message.text)
    await state.set_state(state=PollForm.is_allows_anonymous_answers)

    await message.answer(
        text='Должны ли ответы быть анонимными? "Да" или "Нет"',
        reply_markup=KEYBOARD_YES_NO_CANCEL,
    )


@router.message(PollForm.is_allows_anonymous_answers)
async def add_poll_ask_is_allows_multiple_answers(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает анонимность ответов.
    Спрашивает возможность множественного выбора.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        validate_poll_yes_no(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_YES_NO_CANCEL,
        )
        return

    await state.update_data(is_allows_anonymous_answers=message.text)
    await state.set_state(state=PollForm.is_allows_multiple_answers)

    await message.answer(
        text='Можно ли выбирать несколько ответов? "Да" или "Нет"',
        reply_markup=KEYBOARD_YES_NO_CANCEL,
    )


@router.message(PollForm.is_allows_multiple_answers)
async def add_poll_ask_finish(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает возможность множественного выбора.
    Завершает добавление опроса.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        validate_poll_yes_no(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_YES_NO_CANCEL,
        )
        return

    await state.update_data(is_allows_multiple_answers=message.text)
    poll: dict[str, any] = await state.get_data()

    obj_data: dict[str, any] = {
        # TODO. А если чат изменит имя?.
        'chat_id': await get_chat_id_by_title(title=poll['chat_id']),
        'is_allows_anonymous_answers': True if poll['is_allows_anonymous_answers'] == 'Да' else False,
        'is_allows_multiple_answers': True if poll['is_allows_multiple_answers'] == 'Да' else False,
        'topic': poll['topic'],
        'options': [i.capitalize() for i in poll['options'].split(',')],
        'send_days_of_week_list': translate_days_of_week_from_rus_to_eng(days=poll['days'].split(',')),
        'send_time': time.fromisoformat(poll['time']),
        'title': poll['title'],
        'user_id_telegram': message.from_user.id,
    }

    try:
        async with async_session_maker() as session:
            poll: Poll = await poll_crud.create(
                obj_data=obj_data,
                session=session,
            )
            obj_data['id'] = poll.id

        schedule_poll_sending(poll=poll)

        text: str = f'Опрос добавлен в рассылку!'
        redis_delete(key=RedisKeys.POLL_ALL)
    except Exception as err:
        text: str = f'Произошла ошибка при добавлении опроса!'

    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await asyncio_sleep(1)
    await __cancel(message=message, state=state)


async def __cancel(message: Message, state: FSMContext) -> None:
    """Обрабатывает команду отмены формы создания и возврат в главное меню."""
    state_data: dict[str, any] = await state.get_data()
    await delete_messages_list(
        chat_id=message.chat.id,
        messages_ids=list(range(state_data['_init_message_id'], message.message_id + 2)),
    )
    await state.clear()
    await command_start(message=message, from_command_start=False)
