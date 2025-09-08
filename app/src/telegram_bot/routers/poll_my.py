from asyncio import sleep as async_sleep
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

from app.src.crud.chat import chat_crud
from app.src.crud.poll import poll_crud
from app.src.database.database import async_session_maker
from app.src.telegram_bot.routers.start import command_start
from app.src.scheduler.scheduler import scheduler
from app.src.utils.auth import IsAdmin
from app.src.utils.message import delete_messages_list
from app.src.utils.date import parse_dates_from_text
from app.src.utils.poll import get_all_polls_titles
from app.src.utils.reply_keyboard import (
    RoutersCommands,
    get_keyboard_main_menu,
    make_row_keyboard,
    KEYBOARD_CANCEL,
)

if TYPE_CHECKING:
    from app.src.models.poll import Poll

router: Router = Router()


class MyPollsStatesGroup(StatesGroup):
    """
    Состояния для роутера.
    """
    title = State()
    action = State()
    dates_skip = State()
    resume_days = State()
    _init_message_id: int


@router.message(
    IsAdmin(),
    F.text == RoutersCommands.POLL_MY,
)
async def my_polls_ask_title(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Обрабатывает команду "Мои опросы".

    Показывает список опросов.
    """
    await state.update_data(_init_message_id=message.message_id)

    polls_all_titles: list[str | None] = await get_all_polls_titles()
    if not polls_all_titles:
        await message.answer(text='Нет активных опросов.')
        await async_sleep(1)
        await __cancel(message=message, state=state)
        return

    rows = []
    MAX_ITEMS: int = 2
    for c in range(0, len(polls_all_titles), MAX_ITEMS):
        rows.append(polls_all_titles[c:c + MAX_ITEMS])
    rows.append((RoutersCommands.HOME,))

    await state.set_state(state=MyPollsStatesGroup.title)

    await message.answer(
        text='Какой опрос интересует?',
        reply_markup=make_row_keyboard(rows=rows),
    )


@router.message(MyPollsStatesGroup.title)
async def my_polls_ask_action(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Спрашивает действие для опроса.
    """
    if message.text == RoutersCommands.HOME:
        await __cancel(message=message, state=state)
        return

    async with async_session_maker() as session:
        poll: Poll | None = await poll_crud.retrieve_by_title(obj_title=message.text, session=session)
    if not poll:
        polls_all_titles: list[str | None] = await get_all_polls_titles()
        await message.answer(
            text='Опрос не найден. Нужно выбрать при помощи клавиатуры:',
            reply_markup=make_row_keyboard(rows=(polls_all_titles, (RoutersCommands.HOME,))),
        )
        return

    await state.update_data(title=message.text)
    await state.set_state(state=MyPollsStatesGroup.action)

    poll_data: dict[str, any] = poll.to_dict_repr(
        represent_date_as_str=True,
        represent_time_as_str=True,
        represent_days_of_week_in_rus=True,
    )
    poll_data_dates_skip = [
        f'\n    - {data}'
        for data
        in poll_data['dates_skip']
    ]
    async with async_session_maker() as session:
        chat_title: str = (await chat_crud.retrieve_by_chat_id(obj_chat_id=poll_data['chat_id'], session=session)).title
    await message.answer(
        text=(
            f'Название: {poll_data["title"]}\n'
            f'Тема: {poll_data["topic"]}\n'
            f'Ответы: {poll_data["options"]}\n'
            f'Чат: {chat_title}\n'
            f'Дни: {poll_data["send_days_of_week_list"]}\n'
            f'Время: {poll_data["send_time"][:-3]}\n'
            f'Закрытие опроса через: {poll_data["block_answer_delta_hours"]} часа\n'
            f'Анонимные ответы: {"Да" if poll_data["is_allows_anonymous_answers"] else "Нет"}\n'
            f'Множественные ответы: {"Да" if poll_data["is_allows_multiple_answers"] else "Нет"}\n'
            f'Дни на паузе: {"".join(poll_data_dates_skip) if poll_data_dates_skip else "-"}'
        ),
    )
    await message.answer(
        text='Что нужно сделать?',
        reply_markup=make_row_keyboard(
            # TODO. Вынести в константы.
            rows=(
                ('Возобновить', 'Приостановить', 'Удалить'),
                (RoutersCommands.CANCEL,),
            ),
        ),
    )


@router.message(MyPollsStatesGroup.action)
async def validate_action(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Определяет необходимое действие с опросом.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    if message.text == 'Возобновить':
        return await _validate_action_resume(message=message, state=state)
    elif message.text == 'Приостановить':
        return await _validate_action_pause(message=message, state=state)
    elif message.text == 'Удалить':
        return await _validate_action_delete(message=message, state=state)


@router.message(MyPollsStatesGroup.dates_skip)
async def pause_poll(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Добавляет указанные даты в Poll.dates_skip, чтобы опрос не отправлялся.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        dates: list[str] = parse_dates_from_text(text=message.text)
    except Exception:
        await message.answer(
            text=('Неправильно указаны даты! Попробуйте еще раз.'),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    try:
        async with async_session_maker() as session:
            poll_data: dict[str, any] = await state.get_data()
            poll: Poll = await poll_crud.retrieve_by_title(
                obj_title=poll_data['title'],
                session=session,
            )
            dates.extend(poll.dates_skip)
            dates.sort()
            await poll_crud.update_by_id(
                obj_id=poll.id,
                obj_data={'dates_skip': dates},
                session=session,
                perform_check_unique=False,
            )
    except Exception as err:
        await message.answer(
            text=(f'Произошла ошибка изменения дат:\t{err}'),
            reply_markup=await get_keyboard_main_menu(user_id_telegram=message.from_user.id),
        )

    await message.answer(
        text=('Даты успешно добавлены!'),
        reply_markup=ReplyKeyboardRemove(),
    )
    await async_sleep(1)
    await __cancel(message=message, state=state)


@router.message(MyPollsStatesGroup.resume_days)
async def resume_poll(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Убирает указанные даты из Poll.dates_skip, чтобы опрос отправлялся.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    if message.text != 'Очистить':
        try:
            dates: list[str] = parse_dates_from_text(text=message.text)
        except Exception:
            await message.answer(
                text=('Неправильно указаны даты! Попробуйте еще раз.'),
                reply_markup=KEYBOARD_CANCEL,
            )
            return

    try:
        async with async_session_maker() as session:
            poll_data: dict[str, any] = await state.get_data()
            poll: Poll = await poll_crud.retrieve_by_title(
                obj_title=poll_data['title'],
                session=session,
            )
            if message.text != 'Очистить':
                dates: list[str] = [i for i in poll.dates_skip if i not in dates]
                dates.sort()
            else:
                dates: list = []
            await poll_crud.update_by_id(
                obj_id=poll.id,
                obj_data={'dates_skip': dates},
                session=session,
                perform_check_unique=False,
            )
    except Exception as err:
        await message.answer(
            text=(f'Произошла ошибка изменения дат:\t{err}'),
            reply_markup=await get_keyboard_main_menu(user_id_telegram=message.from_user.id),
        )

    await message.answer(
        text=('Даты успешно удалены!'),
        reply_markup=ReplyKeyboardRemove(),
    )
    await async_sleep(1)
    await __cancel(message=message, state=state)


async def _validate_action_delete(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Удаляет опрос.
    """
    state_data: dict[str, any] = await state.get_data()
    async with async_session_maker() as session:
        poll: Poll = await poll_crud.retrieve_by_title(
            obj_title=state_data['title'],
            session=session,
        )
        await poll_crud.delete_by_id(
            obj_id=poll.id,
            session=session,
        )
        for job in scheduler.get_jobs():
            if job.id.startswith(f'Send poll id={poll.id}'):
                scheduler.remove_job(job_id=job.id)

    await message.answer(
        text='Опрос удален',
        reply_markup=ReplyKeyboardRemove(),
    )
    await async_sleep(1)
    await __cancel(message=message, state=state)


async def _validate_action_pause(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Приостанавливает опрос в указанные даты.
    """
    await message.answer(
        text=(
            'В какие даты отменять опрос? '
            'Например, "01.01, 27.02-30.03, 30.12 - 09.01"'
            '\n\n'
            'Пожалуйста, соблюдайте синтаксис!'
        ),
        reply_markup=KEYBOARD_CANCEL,
    )
    await state.set_state(state=MyPollsStatesGroup.dates_skip)


async def _validate_action_resume(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Возобновляет опрос в указанные даты.
    """
    await message.answer(
        text=(
            'В какие даты нужно возобновить опрос? '
            'Например, "01.01, 02.02" или '
            'интервал "01.01 - 02.02". '
            '\n\n'
            'Пожалуйста, соблюдайте синтаксис!'
            '\n\n'
            'Если нужно убрать все дни отмены, отправьте "Очистить".'
        ),
        reply_markup=make_row_keyboard(
            rows=(
                ('Очистить',),
                ('Отмена',),
            ),
        ),
    )
    await state.set_state(state=MyPollsStatesGroup.resume_days)


async def __cancel(message: Message, state: FSMContext) -> None:
    """Обрабатывает команду отмены просмотра опросов."""
    state_data: dict[str, any] = await state.get_data()
    await delete_messages_list(
        chat_id=message.chat.id,
        messages_ids=list(range(state_data['_init_message_id'], message.message_id + 2)),
    )
    await state.clear()
    await command_start(message=message, from_command_start=False)
