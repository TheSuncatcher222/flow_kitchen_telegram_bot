from typing import TYPE_CHECKING

from asyncio import sleep as async_sleep
from aiogram import (
    Router,
    F,
)
from aiogram.types import Message
from apscheduler.job import Job

from app.src.crud.poll import poll_crud
from app.src.database.database import async_session_maker
from app.src.scheduler.scheduler import scheduler
from app.src.utils.auth import IsDeveloper
from app.src.utils.message import delete_messages_list
from app.src.utils.poll import (
    create_poll_schedule_id,
    schedule_poll_sending,
)
from app.src.utils.reply_keyboard import RoutersCommands

if TYPE_CHECKING:
    from app.src.models.poll import Poll

router: Router = Router()


@router.message(
    IsDeveloper(),
    F.text == RoutersCommands.SYNC_POLL_SCHEDULE,
)
async def sync_poll_schedule(message: Message) -> None:
    """
    Обрабатывает команду "Синхронизировать опросы".
    """
    changes: list[str] = []
    jobs: dict[str, Job] = {job.id: job for job in scheduler.get_jobs() if job.id.startswith('Send poll')}
    async with async_session_maker() as session:
        polls: list[Poll] = await poll_crud.retrieve_all(session=session, limit=None)

    for poll in polls:
        for day in poll.send_days_of_week_list:
            expected_schedule_id: str = create_poll_schedule_id(poll=poll, day=day)
            if expected_schedule_id in jobs:
                del jobs[expected_schedule_id]
            else:
                schedule_poll_sending(poll=poll, specific_day=day)
                changes.append(f'Добавлен опрос "{expected_schedule_id}"')

    for job in jobs.values():
        changes.append(f'Удален опрос "{job.id}"')
        scheduler.remove_job(job_id=job.id)

    if not changes:
        await message.reply(text='Все синхронизировано!')
        await async_sleep(0.5)
    else:
        await message.reply(text='\n'.join(changes))
        await async_sleep(10)

    await delete_messages_list(
        chat_id=message.chat.id,
        messages_ids=list(range(message.message_id, message.message_id + 2)),
    )


@router.message(
    IsDeveloper(),
    F.text == RoutersCommands.DELETE_POLL_SCHEDULE,
)
async def delete_schedule_jobs(message: Message) -> None:
    """
    Обрабатывает команду "Удалить scheduler задачи".
    """
    changes: list[str] = []
    for job in scheduler.get_jobs():
        if job.id.startswith("Send poll"):
            changes.append(f'Удален опрос "{job.id}"')
            scheduler.remove_job(job.id)

    await message.reply(text='\n'.join(changes))
    await async_sleep(10)

    await delete_messages_list(
        chat_id=message.chat.id,
        messages_ids=list(range(message.message_id, message.message_id + 2)),
    )
