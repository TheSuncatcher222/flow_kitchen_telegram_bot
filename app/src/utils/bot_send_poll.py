from aiogram.methods import SendPoll

from app.src.telegram_bot.bot import bot
from app.src.validators.poll import DAYS_RUS_TO_ENG_CRON


async def bot_send_poll(
    chat_id: int,
    question: str,
    options: list[str],
    is_anonymous: bool,
    allows_multiple_answers: bool,
) -> int:
    """
    Отправляет опрос в телеграм чат/группу.
    """
    # TODO. Аннотация
    poll: any = await bot(
        SendPoll(
            chat_id=chat_id,
            question=question,
            options=options,
            is_anonymous=is_anonymous,
            allows_multiple_answers=allows_multiple_answers,
        ),
    )
    return poll.message_id


def parse_poll_cron_params(
    poll_data: dict[str, any],
) -> tuple[str, int, int]:
    """
    Получает параметры задания периодической задачи
    из параметров модели опроса.

    Возвращает кортеж:
        - days_cron: list[str]: список дней недели
        - hour_cron: int: час
        - minute_cron: int: минута
    """
    days: list[str] = poll_data['send_days_of_week_list']
    days_cron: str = ','.join(
        DAYS_RUS_TO_ENG_CRON[day.strip().lower()] for day in days.split(',')
    )
    hour_cron: int = int(poll_data['send_time'].split(':')[0])
    minute_cron: int = int(poll_data['send_time'].split(':')[1])

    return days_cron, hour_cron, minute_cron
