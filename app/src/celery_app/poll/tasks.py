from app.src.celery_app.celery_app import (
    CeleryTasksPriority,
    celery_app,
)
from app.src.database.database import RedisKeys
from app.src.utils.date import get_today_time_data
from app.src.utils.poll import (
    check_if_poll_is_needed_to_send,
    check_if_poll_is_needed_to_stop_answers,
    get_all_polls,
    mark_poll_as_sended,
    send_poll,
    stop_poll,
)
from app.src.utils.redis_data import redis_delete


@celery_app.task(
    name='src.celery_app.poll.tasks.send_polls',
    priority=CeleryTasksPriority.POOL_SEND_POLLS,
)
def send_polls() -> None:
    """
    Получает список опросов из базы данных и отправляет те,
    у которых подошел срок отправки.
    """
    polls: list[dict[str, any] | None] = get_all_polls()
    if len(polls) == 0:
        return

    today_date, today_date_str, today_day_of_week, now_time = get_today_time_data()
    any_changes: bool = False

    for poll_data in polls:
        is_needed_to_send: bool = check_if_poll_is_needed_to_send(
            now_time=now_time,
            poll_data=poll_data,
            today_date_str=today_date_str,
            today_day_of_week=today_day_of_week,
        )
        if is_needed_to_send:
            message_id: int | None = send_poll(poll_data=poll_data)
            mark_poll_as_sended(
                poll_data=poll_data,
                message_id=message_id,
                today_date=today_date,
            )
            any_changes: bool = True

        is_needed_to_stop_answers: bool = check_if_poll_is_needed_to_stop_answers(
            now_time=now_time,
            poll_data=poll_data,
            today_date=today_date,
        )
        if is_needed_to_stop_answers:
            stop_poll(poll_data=poll_data)
            any_changes: bool = True
    
    if any_changes:
        redis_delete(key=RedisKeys.POLL_ALL)

    return
