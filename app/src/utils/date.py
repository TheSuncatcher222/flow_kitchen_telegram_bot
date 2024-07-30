from datetime import (
    date,
    datetime,
    time,
)
import pytz


def get_today_time_data() -> tuple[date, str, str, time]:
    """
    Возвращает текущие:
        - дату: date
        - дату в виде строки: str
        - день недели (eng iso): str
        - время: time
    """
    today_datetime: datetime = datetime.now(pytz.timezone('Europe/Moscow'))
    today_date: date = today_datetime.date()
    today_date_str: str = str(today_datetime.date())
    today_day_of_week: str = today_date.strftime('%A').lower()[:3]
    now_time: time = today_datetime.time()
    return today_date, today_date_str, today_day_of_week, now_time
