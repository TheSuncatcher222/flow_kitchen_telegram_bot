from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import (
    StatesGroup,
    State,
)
from app.src.crud.course import course_crud
from app.src.database.database import async_session_maker
from app.src.telegram_bot.routers.start import command_start
from aiogram.types import Message

from app.src.utils.course import get_all_courses_titles
from app.src.utils.message import delete_messages_list
from app.src.utils.reply_keyboard import (
    RoutersCommands,
    KEYBOARD_COURSE,
    KEYBOARD_COURSE_TARIFF,
    KEYBOARD_HOME,
)

if TYPE_CHECKING:
    from app.src.models.course import Course

router: Router = Router()

class DynamicCourseTitleFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        course_titles = await get_all_courses_titles()
        return message.text in course_titles


class CourseMainForm(StatesGroup):
    """
    Состояния формы роутера.
    """

    selected = State()
    _init_message_id: int
    _course_id: int


@router.message(DynamicCourseTitleFilter())
async def course_description(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Показывает описание курса.
    Запрашивает дальнейшие действия.
    """
    async with async_session_maker() as session:
        course: Course = await course_crud.retrieve_by_title(obj_title=message.text, session=session)

    await state.update_data(_init_message_id=message.message_id)
    await state.update_data(_course_id=course.id)
    await state.set_state(state=CourseMainForm.selected)

    await message.answer_photo(
        photo=course.picture_file_id,
        caption=course.description,
        reply_markup=KEYBOARD_COURSE,
        parse_mode='MarkdownV2',
    )


@router.message(CourseMainForm.selected)
async def validate_action(message: Message, state: FSMContext) -> None:
    """
    Определяет необходимое действие с курсом.
    """
    if message.text == RoutersCommands.HOME:
        return await __cancel(message=message, state=state)
    elif message.text == RoutersCommands.COURSE_TARIFF:
        return await _show_tariffs(message=message, state=state)
    elif message.text == RoutersCommands.COURSE_BUY:
        return await _buy(message=message, state=state)


async def _show_tariffs(message: Message, state: FSMContext) -> None:
    """
    Показывает тарифы курса.
    """
    state_data: dict[str, any] = await state.get_data()
    async with async_session_maker() as session:
        course: Course = await course_crud.retrieve_by_id(obj_id=state_data['_course_id'], session=session)

    await message.answer(
        text=course.tariffs,
        reply_markup=KEYBOARD_COURSE_TARIFF,
        parse_mode='MarkdownV2',
    )


async def _buy(message: Message, state: FSMContext) -> None:
    """
    Покупает курс.
    """
    await message.answer(
        text='Для приобретения курса напишите @sergeypilip',
        reply_markup=KEYBOARD_HOME,
    )


async def __cancel(message: Message, state: FSMContext) -> None:
    """Обрабатывает команду отмены формы создания и возврат в главное меню."""
    state_data: dict[str, any] = await state.get_data()
    await delete_messages_list(
        chat_id=message.chat.id,
        messages_ids=list(range(state_data['_init_message_id'], message.message_id + 2)),
    )
    await state.clear()
    await command_start(message=message, from_command_start=False)
