from datetime import timedelta
from zoneinfo import ZoneInfo

from aiogram.methods import (
    SendPoll,
    StopPoll,
)
from aiogram.types import Message
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from app.src.crud.poll import poll_crud
from app.src.config.config import TimeIntervals
from app.src.database.database import async_session_maker
from app.src.scheduler.scheduler import scheduler
from app.src.models.poll import Poll
from app.src.telegram_bot.bot import bot
from app.src.utils.date import get_today_datetime_data


def create_poll_schedule_id(poll: Poll, day: str) -> str:
    """
    Создает id задачи для отправки опроса в APIScheduler.
    """
    return f'Send poll id={poll.id}, day={day}, hour={poll.send_time.hour}, minute={poll.send_time.minute}'


async def get_all_polls_titles() -> list[str]:
    """
    Возвращает список всех названий опросов.
    """
    async with async_session_maker() as session:
        return [p.title for p in await poll_crud.retrieve_all(session=session)]


async def poll_send(poll_id: int) -> None:
    """
    Отправляет опрос в телеграм чат/группу.
    """
    async with async_session_maker() as session:
        poll: Poll = await poll_crud.retrieve_by_id(
            obj_id=poll_id,
            session=session,
        )

    now_datetime, now_today_date, now_today_date_str, *_ = get_today_datetime_data()

    if poll.last_send_date == now_today_date_str:
        return

    obj_data: dict[str, any] = {'last_send_date': now_today_date}

    if now_today_date_str in poll.dates_skip:
        obj_data.update({
            'dates_skip': [d for d in poll.dates_skip if d != now_today_date_str],
            'is_blocked': True,
        })
    else:
        message: Message = await bot(
            SendPoll(
                chat_id=poll.chat_id,
                question=poll.topic,
                options=poll.options,
                is_anonymous=poll.is_allows_anonymous_answers,
                allows_multiple_answers=poll.is_allows_multiple_answers,
            ),
        )
        obj_data.update({
            'is_blocked': False,
            'message_id': str(message.message_id),
        })
        scheduler.add_job(
            id=f'Block poll id={poll.id}, day={1}',
            trigger=DateTrigger(run_date=now_datetime + timedelta(hours=poll.block_answer_delta_hours)),
            func=poll_block,
            kwargs={'poll_id': poll.id},
            misfire_grace_time=TimeIntervals.SECONDS_IN_1_MINUTE * 30,
        )

    async with async_session_maker() as session:
        await poll_crud.update_by_id(
            obj_id=poll_id,
            obj_data=obj_data,
            session=session,
        )


async def poll_block(poll_id: int) -> None:
    """
    Блокирует опрос.
    """
    async with async_session_maker() as session:
        poll: Poll = await poll_crud.retrieve_by_id(
            obj_id=poll_id,
            session=session,
        )

    if poll.is_blocked:
        return

    await bot(
        StopPoll(
            chat_id=poll.chat_id,
            message_id=poll.message_id,
        ),
    )

    async with async_session_maker() as session:
        await poll_crud.update_by_id(
            obj_id=poll.id,
            obj_data={'is_blocked': True},
            session=session,
        )


def schedule_poll_sending(poll: Poll, specific_day: str | None = None) -> None:
    """
    Создает задачу для cron отправки опроса в APIScheduler.

    Если указан specific_day, то создает задачу только для этого дня.
    """
    for day in poll.send_days_of_week_list:
        if specific_day and specific_day != day:
            continue

        scheduler.add_job(
            id=create_poll_schedule_id(poll=poll, day=day),
            trigger=CronTrigger(
                day_of_week=day,
                hour=poll.send_time.hour,
                minute=poll.send_time.minute,
                timezone=ZoneInfo("Europe/Moscow"),
            ),
            func=poll_send,
            kwargs={'poll_id': poll.id},
            misfire_grace_time=TimeIntervals.SECONDS_IN_1_MINUTE * 30,
        )
