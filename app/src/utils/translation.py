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


def translate_days_of_week_from_rus_to_eng(days: list[str]) -> list[str]:
    """
    Преобразует дни недели из русского в английский.
    """
    return [DAYS_RUS_TO_ENG_CRON[d.lower()] for d in days]


def translate_days_of_week_from_eng_to_rus(days: list[str]) -> list[str]:
    """
    Преобразует дни недели из английского в русский.
    """
    return [DAYS_ENG_CRON_TO_RUS[d.lower()] for d in days]
