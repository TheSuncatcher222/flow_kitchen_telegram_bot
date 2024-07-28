from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def __make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row: list[KeyboardButton] = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(
        keyboard=[row],
        resize_keyboard=True,
    )


KEYBOARD_MAIN_MENU_ADMIN: ReplyKeyboardMarkup = __make_row_keyboard(
    [
        '/add_poll',
    ],
)
