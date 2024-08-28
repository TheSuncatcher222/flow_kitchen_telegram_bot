from aiogram.methods.stop_poll import StopPoll

from app.src.crud.sync_crud.poll_sync_crud import poll_sync_crud
from app.src.database.database import sync_session_maker
from app.src.telegram_bot.bot import bot


async def bot_stop_poll(
    poll_data: dict[str, any],
) -> None:
    """
    Останавливает опрос для ответов в телеграм чате/группе.
    """
    await bot(
        StopPoll(
            chat_id=poll_data['chat_id'],
            message_id=poll_data['message_id'],
        ),
    )
    with sync_session_maker() as session:
        poll_sync_crud.update_by_id(
            obj_id=poll_data['id'],
            obj_data={
                'is_poll_is_blocked': True,
            },
            session=session,
            perform_check_unique=False,
            perform_cleanup=False,
            perform_commit=True,
        )
    return
