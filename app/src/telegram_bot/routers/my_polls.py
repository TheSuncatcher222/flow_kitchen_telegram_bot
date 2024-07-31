from typing import TYPE_CHECKING

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

from app.src.crud.sync_crud.poll_sync_crud import poll_sync_crud
from app.src.database.database import (
    RedisKeys,
    sync_session_maker,
)
from app.src.utils.auth import check_if_user_is_admin
from app.src.utils.poll import (
    get_all_polls,
)
from app.src.utils.redis_data import redis_delete
from app.src.utils.reply_keyboard import (
    make_row_keyboard,
    KEYBOARD_CANCEL,
    KEYBOARD_MAIN_MENU_ADMIN,
)
from app.src.validators.poll import validate_poll_exists

if TYPE_CHECKING:
    from app.src.models.poll import Poll

router: Router = Router()

class MyPollsStatesGroup(StatesGroup):
    """
    Состояния для команды "/my_polls".
    """
    title = State()
    action = State()
    skip_days = State()
    resume_days = State()


@router.message(
    Command('my_polls'),
)
async def my_polls_ask_title(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Обрабатывает команду /my_polls.

    Показывает список опросов.
    Спрашивает название опроса в панели управления.
    """
    if not check_if_user_is_admin(user_id=message.from_user.id):
        return

    all_polls: list[dict[str, any]] = get_all_polls()
    if not all_polls:
        await message.answer(
            text=(
                'Нет опросов'
            ),
            reply_markup=KEYBOARD_MAIN_MENU_ADMIN,
        )
        return

    all_polls_titles = [poll['title'] for poll in all_polls]
    await message.answer(
        text=(
            'Какой опрос вас интересует?'
        ),
        reply_markup=make_row_keyboard(
            items=all_polls_titles,
        ),
    )
    await state.set_state(state=MyPollsStatesGroup.title)
    return


@router.message(
    MyPollsStatesGroup.title,
)
async def my_polls_ask_action(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает название опроса в панели управления.
    Спрашивает даты отмены.
    """
    try:
        validate_poll_exists(value=message.text)
    except ValueError as e:
        all_polls: list[dict[str, any]] = get_all_polls()
        all_polls_titles = [poll['title'] for poll in all_polls]
        await message.answer(
            text=str(e),
            reply_markup=make_row_keyboard(
                items=all_polls_titles,
            ),
        )
        return

    await state.update_data(title=message.text)

    with sync_session_maker() as session:
        poll: Poll = poll_sync_crud.retrieve_by_title(
            obj_title=message.text,
            session=session,
        )
    if poll is None:
        await message.answer(
            text=(
                'Опрос не найден'
            ),
            reply_markup=KEYBOARD_MAIN_MENU_ADMIN,
        )
        return

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
    await message.answer(
        text=(
            f'Название: {poll_data["title"]}\n'
            f'Тема: {poll_data["topic"]}\n'
            f'Ответы: {poll_data["options"]}\n'
            f'Чат: {poll_data["chat_id"]}\n'
            f'Дни: {poll_data["send_days_of_week_list"]}\n'
            f'Время: {poll_data["send_time"]}\n'
            f'Анонимные ответы: {poll_data["is_allows_anonymous_answers"]}\n'
            f'Множественные ответы: {poll_data["is_allows_multiple_answers"]}\n'
            f'Дни на паузе:{"".join(poll_data_dates_skip)}'
        ),
    )

    await message.answer(
        text=(
            'Что нужно сделать?'
        ),
        reply_markup=make_row_keyboard(
            items=[
                'Удалить',
                'Приостановить',
                'Возобновить',
            ],
        ),
    )

    await state.set_state(state=MyPollsStatesGroup.action)
    return


@router.message(
    MyPollsStatesGroup.action,
)
async def validate_action(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Определяет необходимое действие с опросом.
    """
    if message.text == 'Удалить':
        await _validate_action_delete(
            message=message,
            state=state,
        )
    elif message.text == 'Приостановить':
        await _validate_action_pause(
            message=message,
            state=state,
        )
    elif message.text == 'Возобновить':
        await _validate_action_resume(
            message=message,
            state=state,
        )

    # await message.answer(
    #     text=(
    #         'В какие даты отменять опрос? '
    #         'Например, "01.01, 02.02" или '
    #         'интервал "01.01 - 02.02". '
    #         '\n\n'
    #         'Пожалуйста, соблюдайте синтаксис!'
    #         '\n\n'
    #         'Если нужно убрать дни отмены, отправьте "отмена".'
    #     ),
    #     reply_markup=None,
    # )
    # await state.set_state(state=MyPollsStatesGroup.skipp_days)
    # return

async def _validate_action_delete(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Удаляет опрос.
    """
    state_data: dict[str, any] = await state.get_data()
    with sync_session_maker() as session:
        poll: Poll = poll_sync_crud.retrieve_by_title(
            obj_title=state_data['title'],
            session=session,
        )
        poll_sync_crud.delete_by_id(
            obj_id=poll.id,
            session=session,
        )

    await message.answer(
        text=(
            'Опрос удален'
        ),
        reply_markup=KEYBOARD_MAIN_MENU_ADMIN,
    )

    redis_delete(key=RedisKeys.POLL_ALL)


    await state.clear()

    return


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
            'Например, "01.01, 02.02" или '
            'интервал "01.01 - 02.02". '
            '\n\n'
            'Пожалуйста, соблюдайте синтаксис!'
            '\n\n'
            'Если нужно убрать все дни отмены, отправьте "очистить".'
        ),
        reply_markup=make_row_keyboard(
            items=[
                'Очистить',
                'Отмена',
            ],
        ),
    )

    TODO: bool = True
    if TODO:
        await message.answer(
            text=(
                'Функционал еще не завезли ;('
            ),
            reply_markup=KEYBOARD_MAIN_MENU_ADMIN,
        )
        await state.clear()
        return

    await state.set_state(state=MyPollsStatesGroup.skip_days)
    return


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
            'Для отмены нажмите "отмена".'
        ),
        reply_markup=KEYBOARD_CANCEL,
    )

    TODO: bool = True
    if TODO:
        await message.answer(
            text=(
                'Функционал еще не завезли ;('
            ),
            reply_markup=KEYBOARD_MAIN_MENU_ADMIN,
        )
        await state.clear()
        return

    await state.set_state(state=MyPollsStatesGroup.skip_days)
    return
