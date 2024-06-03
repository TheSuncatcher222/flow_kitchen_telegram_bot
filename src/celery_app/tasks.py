import asyncio
from logging import Logger

log = Logger(__name__)

from celery_app.celery_app import celery_app
from db_redis.db_redis import db_redis
from telegram_bot.telegram_bot import bot
from telegram_bot.commands import SendPoll


@celery_app.task(name='celery_task_send_pool')
def celery_task_send_pool():
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(celery_async_part())
    return

async def celery_async_part():
    chat_id = '-4232626901'
    await bot(
        SendPoll(
            chat_id=chat_id,
            question='Будешь сегодня?',
            options=['Да', 'Нет'],
            is_anonymous=False,
            allows_multiple_answers=False,
            explanation='Объяснение',
        )
    )
