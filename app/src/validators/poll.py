from re import fullmatch

from app.src.utils.reply_keyboard import RoutersCommands
from app.src.utils.translation import DAYS_RUS_TO_ENG_CRON


class PollParams:
    """
    Параметры модели опроса.
    """

    # TODO. Свериться с документацией.
    MESSAGE_ID_LEN_MAX: int = 128
    CHAT_ID_LEN_MAX: int = 128
    OPTION_LEN_MAX: int = 100
    SEND_DATE_LEN_MAX: int = 3
    SKIP_DATE_LEN_MAX: int = 2 + 1 + 2 + 1 + 4  # INFO: dd.mm.yyyy
    SEND_TIME_LEN_MAX: int = 2 + 1 + 2
    TITLE_LEN_MAX: int = 100
    TOPIC_LEN_MAX: int = 100


def validate_poll_title(value: str) -> str:
    """
    Валидирует название опроса.
    """
    value: str = value.strip()
    if value.startswith('/'):
        raise ValueError('Название опроса не должно начинаться с "/".')
    if value == RoutersCommands.CANCEL:
        raise ValueError(f'Название опроса не может быть {RoutersCommands.CANCEL}.')
    elif value == RoutersCommands.HOME:
        raise ValueError(f'Название опроса не может быть {RoutersCommands.HOME}.')
    if len(value) > PollParams.TITLE_LEN_MAX:
        raise ValueError(
            'Название опроса для панели управления слишком длинное. '
            f'Максимальная длина - {PollParams.TITLE_LEN_MAX} символов. '
            f'Текущая длина - {len(value)} символов.',
        )
    return value

def validate_poll_topic(value: str) -> str:
    """
    Валидирует тему опроса.
    """
    if value.strip().startswith('/'):
        raise ValueError('Тема опроса не должна начинаться с "/".')
    if len(value) > PollParams.TOPIC_LEN_MAX:
        raise ValueError(
            'Тема опроса для панели управления слишком длинная. '
            f'Максимальная длина - {PollParams.TOPIC_LEN_MAX} символов. '
            f'Текущая длина - {len(value)} символов.',
        )
    return value


def validate_poll_options(value: str) -> list[str]:
    """
    Валидирует варианты ответов.
    """
    options: list[str] = value.split(',')
    if len(options) < 2 or len(options) > 10:
        raise ValueError('Необходимо указать от 2 до 10 вариантов ответов.')
    for option in options:
        if option.strip().startswith('/'):
            raise ValueError('Варианты ответов не должны начинаться с "/".')
        if len(option) > PollParams.OPTION_LEN_MAX:
            raise ValueError(
                'Варианты ответов для панели управления слишком длинные. '
                f'Максимальная длина - {PollParams.OPTION_LEN_MAX} символов. '
                f'Текущая максимальная длина - {len(option)} символов.',
            )
    return options


async def validate_poll_chat_id(value: str) -> str:
    """
    Валидирует чат ID.
    """
    # INFO. Циклический импорт.
    from app.src.utils.chat import get_chat_all_titles

    if value not in await get_chat_all_titles():
        raise ValueError('Телеграм чат с таким названием недоступен.')
    return value


def validate_poll_days(value: str) -> list[str]:
    """
    Валидирует дни опроса.
    """
    days: list[str] = value.split(',')
    for day in days:
        if day.lower() not in DAYS_RUS_TO_ENG_CRON:
            raise ValueError(
                'Дни недели необходимо указывать кратко через запятую. '
                'Допустимые значения: "пн", "вт", "ср", "чт", "пт", "сб", "вс".',
            )
    return days

def validate_poll_time(value: str) -> str:
    """
    Валидирует время опроса.
    """
    value: str = value.lower().strip()
    if not fullmatch(r'\d{2}:\d{2}', value):
        raise ValueError('Время опроса должно быть в формате "чч:мм".')
    hours, minutes = map(int, value.split(':'))
    if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
        raise ValueError('Время опроса должно быть в формате "чч:мм".')
    return value


def validate_poll_yes_no(value: str) -> str:
    """
    Валидирует значение "да"/"нет".
    """
    value: str = value.lower().strip()
    if value not in ('да', 'нет'):
        raise ValueError('Значение должно быть либо "да", либо "нет".')
    return value
