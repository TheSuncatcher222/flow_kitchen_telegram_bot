import asyncio
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)

from app.src.config.config import settings
from app.src.crud.sync_crud.poll_sync_crud import poll_sync_crud
from app.src.database.database import (
    RedisKeys,
    sync_session_maker,
)
from app.src.models.poll import Poll
from app.src.utils.bot_send_poll import bot_send_poll
from app.src.utils.bot_stop_poll import bot_stop_poll
from app.src.utils.redis_data import (
    redis_get,
    redis_set,
)

def check_if_poll_is_needed_to_send(
    now_time: time,
    poll_data: dict[str, any],
    today_date_str: str,
    today_day_of_week: str,
) -> bool:
    """
    Проверяет, нужно ли отправлять опрос.
    """
    if poll_data['last_send_date'] == today_date_str:
        return False

    if today_date_str in poll_data['dates_skip']:
        return False

    if (
        today_day_of_week in poll_data['send_days_of_week_list']
        and
        now_time >= time.fromisoformat(poll_data['send_time'])
    ):
        return True

    return False


def check_if_poll_is_needed_to_stop_answers(
    now_time: time,
    poll_data: dict[str, any],
    today_date: date,
) -> bool:
    """
    Проверяет, нужно ли останавливать опрос.
    """
    block_answer_delta_hours: int | None = poll_data['block_answer_delta_hours']

    if (
        not block_answer_delta_hours
        or
        poll_data['is_poll_is_blocked']
        or
        (
            not poll_data['last_send_date']
            or
            poll_data['last_send_date'] == 'None'
        )

    ):
        return False

    last_send_datetime: datetime = datetime.combine(
        date=date.fromisoformat(poll_data['last_send_date']),
        time=time.fromisoformat(poll_data['send_time']),
    )
    now_datetime: datetime = datetime.combine(
        date=today_date,
        time=now_time,
    )
    if now_datetime > last_send_datetime + timedelta(hours=block_answer_delta_hours):
        stop_poll(poll_data=poll_data)
        return True

    return False


def get_all_polls() -> list[dict[str, any]]:
    """
    Возвращает список всех опросов из базы данных.
    """
    if not settings.DEBUG_POLL_CACHE:
        all_polls: None | dict[list[dict[str, any]]] = redis_get(key=RedisKeys.POLL_ALL)
        if isinstance(all_polls, dict):
            return all_polls['all_polls']

    with sync_session_maker() as session:
        polls: list[Poll] = poll_sync_crud.retrieve_all(session=session)

    if len(polls) == 0:
        redis_set(
            key=RedisKeys.POLL_ALL,
            value={'all_polls': []},
        )

    all_polls: list[dict[str, any]] = parse_polls_to_redis(polls=polls)
    redis_set(
        key=RedisKeys.POLL_ALL,
        value={'all_polls': all_polls},
    )

    return all_polls


def send_poll(poll_data: dict[str, any]) -> int | None:
    """
    Отправляет опрос в телеграм чат.
    """
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop.is_closed():
        loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=loop)

    try:
        poll_id: int = loop.run_until_complete(
            bot_send_poll(
                chat_id=poll_data['chat_id'],
                question=poll_data['topic'],
                options=poll_data['options'],
                is_anonymous=poll_data['is_allows_anonymous_answers'],
                allows_multiple_answers=poll_data['is_allows_multiple_answers'],
            ),
        )

    except Exception as err:
        # TODO. Обработать ошибку.
        poll_id: None = None

    finally:
        # TODO. Отправить сообщение в телеграм чат.
        pass

    return poll_id


def stop_poll(poll_data: dict[str, any]) -> None:
    """
    Останавливает опрос в телеграм чате.
    """
    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    if loop.is_closed():
        loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=loop)

    try:
        loop.run_until_complete(
            bot_stop_poll(poll_data=poll_data),
        )

    except Exception as err:
        # TODO. Обработать ошибку.
        pass

    finally:
        # TODO. Отправить сообщение в телеграм чат.
        pass

    return


def mark_poll_as_sended_and_unblocked(
    poll_data: dict[str, any],
    message_id: int,
    today_date: date,
) -> None:
    with sync_session_maker() as session:
        poll_sync_crud.update_by_id(
            obj_id=poll_data['id'],
            obj_data={
                'last_send_date': today_date,
                'message_id': message_id,
                'is_poll_is_blocked': False,
            },
            session=session,
            perform_check_unique=False,
            perform_cleanup=False,
            perform_commit=True,
        )
    return


def parse_polls_to_redis(polls: list[Poll]) -> list[dict[str, any]]:
    """
    Преобразует тип данных list[Poll] в list[dict[str, any]].
    """
    return [
        poll.to_dict_repr(
            represent_date_as_str=True,
            represent_time_as_str=True,
        )
        for poll
        in polls
    ]
