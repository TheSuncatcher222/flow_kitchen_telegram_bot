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
from aiogram.utils.text_decorations import markdown_decoration

from app.src.crud.course import course_crud
from app.src.database.database import async_session_maker
from app.src.telegram_bot.routers.start import command_start
from app.src.utils.auth import IsAdmin
from app.src.utils.message import delete_messages_list
from app.src.utils.course import get_all_courses_titles
from app.src.utils.reply_keyboard import (
    RoutersCommands,
    make_row_keyboard,
    KEYBOARD_YES_CANCEL,
    KEYBOARD_CANCEL,
)
from app.src.validators.course import (
    validate_course_description,
    validate_course_keyboard_coordinates,
    validate_course_picture,
    validate_course_tariffs,
    validate_course_title,
)

if TYPE_CHECKING:
    from app.src.models.course import Course

router: Router = Router()


class MyCoursesStatesGroup(StatesGroup):
    """
    Состояния для роутера.
    """
    title = State()
    action = State()
    change_title = State()
    change_description = State()
    change_photo = State()
    change_tariffs = State()
    change_keyboard_coordinates = State()
    delete = State()
    _init_message_id: int
    _course_id: int


@router.message(
    IsAdmin(),
    F.text == RoutersCommands.COURSE_MY,
)
async def my_course_ask_title(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Обрабатывает команду "Мои курсы".

    Показывает список курсов.
    """
    await state.update_data(_init_message_id=message.message_id)

    courses_all_titles: list[str | None] = await get_all_courses_titles()
    if not courses_all_titles:
        await message.answer(text='Нет активных курсов.')
        await async_sleep(1)
        return await __cancel(message=message, state=state)

    rows = []
    MAX_ITEMS: int = 2
    for c in range(0, len(courses_all_titles), MAX_ITEMS):
        rows.append(courses_all_titles[c:c + MAX_ITEMS])
    rows.append((RoutersCommands.HOME,))

    await state.set_state(state=MyCoursesStatesGroup.title)

    await message.answer(
        text='Какой курс интересует?',
        reply_markup=make_row_keyboard(rows=rows),
    )



@router.message(MyCoursesStatesGroup.title)
async def my_course_ask_action(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Спрашивает действие для курса.
    """
    if message.text == RoutersCommands.HOME:
        return await __cancel(message=message, state=state)

    async with async_session_maker() as session:
        course: Course | None = await course_crud.retrieve_by_title(obj_title=message.text, session=session)
    if not course:
        courses_all_titles: list[str | None] = await get_all_courses_titles()
        await message.answer(
            text='Курс не найден. Нужно выбрать при помощи клавиатуры:',
            reply_markup=make_row_keyboard(rows=(courses_all_titles, (RoutersCommands.HOME,))),
        )
        return

    await state.update_data(title=message.text)
    await state.update_data(_course_id=course.id)
    await state.set_state(state=MyCoursesStatesGroup.action)

    course_data: dict[str, any] = course.to_dict_repr()
    await message.answer_photo(
        photo=course_data['picture_file_id'],
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        text=course_data['description'],
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='MarkdownV2',
    )
    await message.answer(
        text=course_data['tariffs'],
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='MarkdownV2',
    )
    await message.answer(
        text=f'координаты на клавиатуре: {course_data["keyboard_coordinates"]}',
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        text='Что нужно сделать?',
        reply_markup=make_row_keyboard(
            # TODO. Вынести в константы.
            rows=(
                ('Изменить название', 'Изменить описание'),
                ('Изменить тарифы', 'Изменить картинку'),
                ('Изменить координаты на клавиатуре',),
                ('Удалить',),
                (RoutersCommands.CANCEL,),
            ),
        ),
    )


@router.message(MyCoursesStatesGroup.action)
async def validate_action(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Определяет необходимое действие с опросом.
    """
    if message.text == RoutersCommands.CANCEL:
        return await __cancel(message=message, state=state)
    elif message.text == 'Изменить название':
        return await _validate_action_change_title(message=message, state=state)
    elif message.text == 'Изменить описание':
        return await _validate_action_change_description(message=message, state=state)
    elif message.text == 'Изменить тарифы':
        return await _validate_action_change_tariffs(message=message, state=state)
    elif message.text == 'Изменить картинку':
        return await _validate_action_change_photo(message=message, state=state)
    elif message.text == 'Изменить координаты на клавиатуре':
        return await _validate_action_change_keyboard_coordinates(message=message, state=state)
    elif message.text == 'Удалить':
        return await _validate_action_delete(message=message, state=state)


# TODO. Очень много задвоения кода в my_course_change_*


@router.message(MyCoursesStatesGroup.change_title)
async def my_course_change_title(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Изменяет название курса.
    """
    if message.text == RoutersCommands.CANCEL:
        return await __cancel(message=message, state=state)

    try:
        title: str = await validate_course_title(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    async with async_session_maker() as session:
        await course_crud.update_by_id(
            obj_id=(await state.get_data())['_course_id'],
            obj_data={'title': title},
            session=session,
        )

    await message.answer(
        text='Название курса изменено.',
        reply_markup=ReplyKeyboardRemove(),
    )
    await async_sleep(1)
    await __cancel(message=message, state=state)


@router.message(MyCoursesStatesGroup.change_description)
async def my_course_change_description(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Изменяет описание курса.
    """
    if message.text == RoutersCommands.CANCEL:
        return await __cancel(message=message, state=state)

    try:
        if message.caption:
            raise ValueError('Нужно указать описание курса без прикрепления картинки')
        validate_course_description(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    async with async_session_maker() as session:
        await course_crud.update_by_id(
            obj_id=(await state.get_data())['_course_id'],
            obj_data={'description': markdown_decoration.unparse(text=message.text, entities=message.entities)},
            session=session,
        )

    await message.answer(
        text='Описание курса изменено.',
        reply_markup=ReplyKeyboardRemove(),
    )
    await async_sleep(1)
    await __cancel(message=message, state=state)


@router.message(MyCoursesStatesGroup.change_tariffs)
async def my_course_change_tariffs(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Изменяет описание тарифов курса.
    """
    if message.text == RoutersCommands.CANCEL:
        return await __cancel(message=message, state=state)

    try:
        validate_course_tariffs(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    async with async_session_maker() as session:
        await course_crud.update_by_id(
            obj_id=(await state.get_data())['_course_id'],
            obj_data={'tariffs': markdown_decoration.unparse(text=message.text, entities=message.entities)},
            session=session,
        )

    await message.answer(
        text='Описание тарифов курса изменено.',
        reply_markup=ReplyKeyboardRemove(),
    )
    await async_sleep(1)
    await __cancel(message=message, state=state)


@router.message(MyCoursesStatesGroup.change_photo)
async def my_course_change_photo(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Изменяет описание тарифов курса.
    """
    if message.text == RoutersCommands.CANCEL:
        return await __cancel(message=message, state=state)

    try:
        if not message.photo:
            raise ValueError('Нужно загрузить картинку')
        picture_file_id: str = validate_course_picture(value=message.photo[-1])
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    async with async_session_maker() as session:
        await course_crud.update_by_id(
            obj_id=(await state.get_data())['_course_id'],
            obj_data={'picture_file_id': picture_file_id},
            session=session,
        )

    await message.answer(
        text='Картинка курса изменена.',
        reply_markup=ReplyKeyboardRemove(),
    )
    await async_sleep(1)
    await __cancel(message=message, state=state)


@router.message(MyCoursesStatesGroup.change_keyboard_coordinates)
async def my_course_change_keyboard_coordinates(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Изменяет описание тарифов курса.
    """
    if message.text == RoutersCommands.CANCEL:
        return await __cancel(message=message, state=state)

    try:
        keyboard_coordinates: str = await validate_course_keyboard_coordinates(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    async with async_session_maker() as session:
        await course_crud.update_by_id(
            obj_id=(await state.get_data())['_course_id'],
            obj_data={'keyboard_coordinates': keyboard_coordinates},
            session=session,
        )

    await message.answer(
        text='Координаты курса на клавиатуре изменены.',
        reply_markup=ReplyKeyboardRemove(),
    )
    await async_sleep(1)
    await __cancel(message=message, state=state)


@router.message(MyCoursesStatesGroup.delete)
async def my_course_delete(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Удаляет курс.
    """
    if message.text == RoutersCommands.CANCEL:
        return await __cancel(message=message, state=state)
    elif message.text != RoutersCommands.YES:
        await message.answer(
            text='Для подтверждения удаления нажмите кнопку "Да".',
            reply_markup=KEYBOARD_YES_CANCEL,
        )
        return

    state_data: dict[str, any] = await state.get_data()
    async with async_session_maker() as session:
        course: Course = await course_crud.retrieve_by_title(
            obj_title=state_data['title'],
            session=session,
        )
        await course_crud.delete_by_id(
            obj_id=course.id,
            session=session,
        )

    await message.answer(
        text='Курс удален',
        reply_markup=ReplyKeyboardRemove(),
    )
    await async_sleep(1)
    await __cancel(message=message, state=state)


# TODO. Это не приватные методы, надо переименовать.
#       Например, my_course_change_title and my_course_change_title_complete
async def _validate_action_change_title(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Запрашивает новое название курса.
    """
    await state.set_state(state=MyCoursesStatesGroup.change_title)

    await message.answer(
        text='Как будет называться курс? Например, "Hip-Hop Advanced"',
        reply_markup=KEYBOARD_CANCEL,
    )


async def _validate_action_change_description(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Запрашивает новое описание курса.
    """
    await state.set_state(state=MyCoursesStatesGroup.change_description)

    await message.answer(
        text='Какое будет описание курса? Можно длинный текст с разным форматированием',
        reply_markup=KEYBOARD_CANCEL,
    )


async def _validate_action_change_tariffs(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Запрашивает новое описание тарифов курса.
    """
    await state.set_state(state=MyCoursesStatesGroup.change_tariffs)

    await message.answer(
        text='Какие будут тарифы курса? Можно длинный текст с разным форматированием',
        reply_markup=KEYBOARD_CANCEL,
    )


async def _validate_action_change_keyboard_coordinates(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Запрашивает новые координаты курса на клавиатуре.
    """
    await state.set_state(state=MyCoursesStatesGroup.change_keyboard_coordinates)

    await message.answer(
        text=(
            'Какие будут координаты кнопки на клавиатуре? Укажи цифрами в формате "ряд столбец"'
            '\n\n'
            'Например, если у курсов указано:\n'
            '"1 80" (A), "5 4" (Б), "1 1" (В), "1 2" (Г), "10 10" (Д)\n\n'
            'То кнопки будут такие:\n'
            '[В] [Г] [А]\n'
            '[      Б      ]\n'
            '[      Д      ]'
        ),
        reply_markup=KEYBOARD_CANCEL,
    )


async def _validate_action_change_photo(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Запрашивает новую картинку курса.
    """
    await state.set_state(state=MyCoursesStatesGroup.change_photo)

    await message.answer(
        text='Какая будет картинка курса? Загрузи сюда изображение до 1080x1080',
        reply_markup=KEYBOARD_CANCEL,
    )


async def _validate_action_delete(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Запрашивает подтверждение удаления курса.
    """
    await state.set_state(state=MyCoursesStatesGroup.delete)

    await message.answer(
        text='Вы действительно хотите безвозвратно удалить курс?',
        reply_markup=KEYBOARD_YES_CANCEL,
    )


async def __cancel(message: Message, state: FSMContext) -> None:
    """Обрабатывает команду отмены просмотра опросов."""
    state_data: dict[str, any] = await state.get_data()
    await delete_messages_list(
        chat_id=message.chat.id,
        messages_ids=list(range(state_data['_init_message_id'], message.message_id + 2)),
    )
    await state.clear()
    await command_start(message=message, from_command_start=False)
