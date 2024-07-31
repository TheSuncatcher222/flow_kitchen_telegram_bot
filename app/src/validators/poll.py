from re import fullmatch

# from app.src.utils.chat import get_chat_all_titles
# from app.src.utils.poll import get_all_polls

class PollParams:

    # TODO. Свериться с документацией.
    CHAT_ID_LEN_MAX: int = 128
    OPTION_LEN_MAX: int = 100
    SEND_DATE_LEN_MAX: int = 3
    SEND_TIME_LEN_MAX: int = 2 + 1 + 2
    TITLE_LEN_MAX: int = 100
    TOPIC_LEN_MAX: int = 100


DAYS_RUS_TO_ENG_CRON: dict[str, str] = {
    'пн': 'mon',
    'вт': 'tue',
    'ср': 'wed',
    'чт': 'thu',
    'пт': 'fri',
    'сб': 'sat',
    'вс': 'sun',
}
DAYS_ENG_CRON_TO_RUS: dict[str, str] = {
    'mon': 'пн',
    'tue': 'вт',
    'wed': 'ср',
    'thu': 'чт',
    'fri': 'пт',
    'sat': 'сб',
    'sun': 'вс',
}


def validate_poll_exists(value: str) -> str:
    """
    Валидирует существование опроса.
    """
    # all_polls: list[dict[str, any]] = get_all_polls()
    # all_polls_titles = [poll['title'] for poll in all_polls]
    # if value not in all_polls_titles():
    #     raise ValueError(
    #         'Опрос не найден. Попробуйте ещё раз.'
    #     )
    return value


def validate_poll_title(value: str) -> str:
    """
    Валидирует название опроса.
    """
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
        raise ValueError(
            'Необходимо указать от 2 до 10 вариантов ответов.',
        )
    for option in options:
        if len(option) > PollParams.OPTION_LEN_MAX:
            raise ValueError(
                'Варианты ответов для панели управления слишком длинные. '
                f'Максимальная длина - {PollParams.OPTION_LEN_MAX} символов. '
                f'Текущая максимальная длина - {len(option)} символов.',
            )
    return options


def validate_poll_chat_id(value: str) -> str:
    """
    Валидирует чат ID.
    """
    # if value not in get_chat_all_titles():
    #     raise ValueError(
    #         'Телеграм чат с таким названием недоступен.'
    #     )
    return value


def validate_poll_days(value: str) -> list[str]:
    """
    Валидирует дни опроса.
    """
    days: list[str] = value.split(',')
    for day in days:
        if day.lower() not in DAYS_RUS_TO_ENG_CRON:
            raise ValueError(
                'Дни недели необходимо указанывать кратко через запятую. '
                'Допустимые значения: "пн", "вт", "ср", "чт", "пт", "сб", "вс".',
            )
    return days

def validate_poll_time(value: str) -> str:
    """
    Валидирует время опроса.
    """
    if not fullmatch(r'\d{2}:\d{2}', value):
        raise ValueError(
            'Время опроса должно быть в формате "чч:мм".',
        )
    return value

def validate_poll_yes_no(value: str) -> str:
    """
    Валидирует значение "да"/"нет".
    """
    if value.lower() not in ('да', 'нет'):
        raise ValueError(
            'Значение должно быть либо "да", либо "нет".',
        )
    return value
