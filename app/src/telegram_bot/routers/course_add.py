from asyncio import sleep as async_sleep

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
from app.src.utils.reply_keyboard import (
    RoutersCommands,
    KEYBOARD_CANCEL,
)
from app.src.validators.course import (
    validate_course_description,
    validate_course_keyboard_coordinates,
    validate_course_picture,
    validate_course_tariffs,
    validate_course_title,
)

router: Router = Router()


class Form(StatesGroup):
    """
    Состояния формы роутера.
    """

    title = State()
    description = State()
    picture_file_id = State()
    tariffs = State()
    keyboard_coordinates = State()
    _init_message_id: int


@router.message(
    IsAdmin(),
    F.text == RoutersCommands.COURSE_ADD,
)
async def course_add_ask_title(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Инициализирует форму создания курса.
    Спрашивает название.
    """
    await state.update_data(_init_message_id=message.message_id)
    await state.set_state(state=Form.title)

    await message.answer(
        text='Как будет называться курс? Например, "Hip-Hop Advanced"',
        reply_markup=KEYBOARD_CANCEL,
    )


@router.message(Form.title)
async def course_add_ask_description(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает название курса.
    Спрашивает описание.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        title: str = await validate_course_title(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    await state.update_data(title=title)
    await state.set_state(state=Form.description)

    await message.answer(
        text='Какое будет описание курса? Можно длинный текст с разным форматированием',
        reply_markup=KEYBOARD_CANCEL,
    )


@router.message(Form.description)
async def course_add_ask_picture(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает описание курса.
    Спрашивает картинку.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        validate_course_description(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    await state.update_data(description=markdown_decoration.unparse(text=message.text, entities=message.entities))
    await state.set_state(state=Form.picture_file_id)

    await message.answer(
        text='Какая будет картинка курса? Загрузи сюда изображение до 1080x1080',
        reply_markup=KEYBOARD_CANCEL,
    )


@router.message(Form.picture_file_id)
async def course_add_ask_tariffs(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает картинку курса.
    Спрашивает тарифы.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

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

    await state.update_data(picture_file_id=picture_file_id)
    await state.set_state(state=Form.tariffs)

    await message.answer(
        text='Какие будут тарифы курса? Можно длинный текст с разным форматированием',
        reply_markup=KEYBOARD_CANCEL,
    )


@router.message(Form.tariffs)
async def course_add_ask_keyboard_coordinates(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает тарифы курса.
    Спрашивает координаты.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        validate_course_tariffs(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    await state.update_data(tariffs=markdown_decoration.unparse(text=message.text, entities=message.entities))
    await state.set_state(state=Form.keyboard_coordinates)

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


@router.message(Form.keyboard_coordinates)
async def course_add_complete(
    message: Message,
    state: FSMContext,
) -> None:
    """
    Устанавливает координаты курса.
    Завершает форму создания.
    """
    if message.text == RoutersCommands.CANCEL:
        await __cancel(message=message, state=state)
        return

    try:
        keyboard_coordinates: str = await validate_course_keyboard_coordinates(value=message.text)
    except ValueError as e:
        await message.answer(
            text=str(e),
            reply_markup=KEYBOARD_CANCEL,
        )
        return

    await state.update_data(keyboard_coordinates=keyboard_coordinates)

    state_data: dict[str, any] = await state.get_data()

    try:
        async with async_session_maker() as session:
            await course_crud.create(
                obj_data={
                    'title': state_data['title'],
                    'description': state_data['description'],
                    'picture_file_id': state_data['picture_file_id'],
                    'tariffs': state_data['tariffs'],
                    'keyboard_coordinates': state_data['keyboard_coordinates'],
                    'user_id_telegram': message.from_user.id,
                },
                session=session,
            )
        text='Курс успешно создан!'
    except Exception as err:
        text: str = f'Произошла ошибка при добавлении курса!'
    await message.answer(
        text=text,
        reply_markup=ReplyKeyboardRemove(),
    )
    await async_sleep(1)
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
