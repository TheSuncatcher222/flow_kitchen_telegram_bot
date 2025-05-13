from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.src.utils.auth import (
    check_if_user_is_admin,
    check_if_user_is_developer,
)
from app.src.utils.course import get_all_courses_for_keyboard


class RoutersCommands:
    """
    Класс хранения списка команд.
    """

    # Common
    CANCEL: str = 'Отмена'
    HOME: str = 'Главное меню'
    YES: str = 'Да'
    NO: str = 'Нет'

    # Admin
    DELETE: str = 'Удалить'

    # Developer
    REDIS_CLEAR: str = '⛔️ Очистить Redis'
    SYNC_POLL_SCHEDULE: str = '⛔️ Синхронизировать опросы'

    # Course
    COURSE_ADD: str = '⚠️ Добавить курс'
    COURSE_MY: str = '⚠️ Мои курсы'
    COURSE_TARIFF: str = 'Тарифы и цены'
    COURSE_BUY: str = 'Приобрести курс'

    # Poll
    POLL_ADD: str = '⚠️ Добавить опрос'
    POLL_MY: str = '⚠️ Мои опросы'


def make_row_keyboard(rows: tuple[tuple[str]]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один/несколько ряд(ов)
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    keyboard: list[list[KeyboardButton]] = []
    for row in rows:
        keyboard.append(KeyboardButton(text=item) for item in row)
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )


async def get_keyboard_main_menu(user_id_telegram: int | str) -> ReplyKeyboardMarkup:
    """
    Возвращает клавиатуру главного меню.
    """
    # TODO. Добавить Redis
    courses: dict[str, str] = await get_all_courses_for_keyboard()
    grid: dict[int, list[tuple[int, str]]] = {}
    for title, coordinate in courses.items():
        row, col = map(int, coordinate.split())
        grid.setdefault(row, []).append((col, title))
    keyboard: list[list[str]] = list([title for _, title in sorted(grid[row])] for row in sorted(grid))

    if check_if_user_is_developer(user_id_telegram=user_id_telegram):
        keyboard: list[list[str]] = [
            [RoutersCommands.REDIS_CLEAR],
            [RoutersCommands.SYNC_POLL_SCHEDULE],
            [RoutersCommands.COURSE_ADD, RoutersCommands.COURSE_MY],
            [RoutersCommands.POLL_ADD, RoutersCommands.POLL_MY],
            *keyboard,
        ]
    elif check_if_user_is_admin(user_id_telegram=user_id_telegram):
        keyboard: list[list[str]] = [
            [RoutersCommands.COURSE_ADD, RoutersCommands.COURSE_MY],
            [RoutersCommands.POLL_ADD, RoutersCommands.POLL_MY],
            *keyboard,
        ]

    return make_row_keyboard(rows=keyboard)

KEYBOARD_CANCEL: ReplyKeyboardMarkup = make_row_keyboard(rows=((RoutersCommands.CANCEL,),))
KEYBOARD_HOME: ReplyKeyboardMarkup = make_row_keyboard(rows=((RoutersCommands.HOME,),))
KEYBOARD_YES_NO: ReplyKeyboardMarkup = make_row_keyboard(rows=((RoutersCommands.YES, RoutersCommands.NO),))
KEYBOARD_YES_NO_CANCEL: ReplyKeyboardMarkup = make_row_keyboard(rows=((RoutersCommands.YES, RoutersCommands.NO), (RoutersCommands.CANCEL,)))
KEYBOARD_YES_CANCEL: ReplyKeyboardMarkup = make_row_keyboard(rows=((RoutersCommands.YES,), (RoutersCommands.CANCEL,)))
KEYBOARD_COURSE: ReplyKeyboardMarkup = make_row_keyboard(rows=((RoutersCommands.COURSE_TARIFF,), (RoutersCommands.COURSE_BUY,), (RoutersCommands.HOME,)))
KEYBOARD_COURSE_TARIFF: ReplyKeyboardMarkup = make_row_keyboard(rows=((RoutersCommands.COURSE_BUY,), (RoutersCommands.HOME,)))
