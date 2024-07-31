
from app.src.validators.poll import (
    DAYS_RUS_TO_ENG_CRON,
    DAYS_ENG_CRON_TO_RUS,
)


def translate_days_of_week_from_rus_to_eng(
    send_days_of_week_list: list[str],
) -> list[str]:
    """
    Преобразует дни недели из русского в английский.
    """
    return [DAYS_RUS_TO_ENG_CRON[day.lower()] for day in send_days_of_week_list]


def translate_days_of_week_from_eng_to_rus(
    send_days_of_week_list: list[str],
) -> list[str]:
    """
    Преобразует дни недели из английского в русский.
    """
    return [DAYS_ENG_CRON_TO_RUS[day.lower()] for day in send_days_of_week_list]
