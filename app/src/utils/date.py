from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
import pytz


def get_today_time_data() -> tuple[date, str, str, time]:
    """
    Возвращает текущие:
        - дату: date (2024-11-28)
        - дату в виде строки: str (2024-11-28)
        - день недели (eng iso): str (thu)
        - время: time (19:55:11.748060)
    """
    today_datetime: datetime = datetime.now(pytz.timezone('Europe/Moscow'))
    today_date: date = today_datetime.date()
    today_date_str: str = str(today_datetime.date())
    today_day_of_week: str = today_date.strftime('%A').lower()[:3]
    now_time: time = today_datetime.time()
    return today_date, today_date_str, today_day_of_week, now_time


def parse_dates_from_text(text: str) -> list[str]:
    """
    Преобразует даты из строки формата "DD.MM, DD.MM-DD.MM, DD.MM - DD.MM"
    в список ближайших непрошедших дат формата "YYYY-MM-DD".

    Например,
        '27.11 - 29.11, 29.11, 31.12-03.01'
    конвертируется в
        ['2024-11-29', '2024-12-31', '2025-01-01', '2025-01-02',
         '2025-01-03', '2025-11-27', '2025-11-28', '2025-11-29']
    """
    today_datetime: datetime = datetime.now(pytz.timezone('Europe/Moscow'))
    today_date: date = today_datetime.date()
    today_year: int = today_date.year

    dates_raw = [date.strip() for date in text.split(',')]
    dates_result: list[date] = []
    for item in dates_raw:
        if '-' in item:
            dates_result.extend(
                __parse_range(
                        date_range_str=item,
                        today_date=today_date,
                        today_year=today_year,
                ),
            )
        else:
            dates_result.append(
                __parse_date(
                    date_str=item,
                    today_date=today_date,
                    today_year=today_year,
                ),
            )

    dates_result.sort()
    return [str(d) for d in dates_result]


def __parse_date(
    date_str: str,
    today_date: date,
    today_year: int,
) -> date:
    """
    Преобразует дату из формата "DD.MM"
    в ближайшую не прошедшую дату формата YYYY-MM-DD.
    """
    day, month = date_str.split('.')
    year: int = today_year
    result_date: date = date(year=today_year, month=int(month), day=int(day))
    while result_date < today_date:
        year += 1
        result_date = date(year=year, month=int(month), day=int(day))
    return result_date


def __parse_range(
    date_range_str: str,
    today_date: date,
    today_year: int,
) -> list[date]:
    """
    Преобразует диапазон дат из формата "DD.MM"
    в перечень ближайших не прошедших дат формата YYYY-MM-DD.
    """
    start_date: date = __parse_date(
        today_date=today_date,
        today_year=today_year,
        date_str=date_range_str.split('-')[0],
    )
    end_date: date = __parse_date(
        today_date=today_date,
        today_year=today_year,
        date_str=date_range_str.split('-')[1],
    )
    while end_date < start_date:
        end_date = date(year=end_date.year + 1, month=end_date.month, day=end_date.day)

    dates: list[date] = []
    next_date: date = start_date
    while next_date <= end_date:
        dates.append(next_date)
        next_date += timedelta(days=1)

    return dates
