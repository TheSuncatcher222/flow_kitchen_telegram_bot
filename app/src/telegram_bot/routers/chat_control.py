from aiogram import Router
from aiogram.filters import (
    ChatMemberUpdatedFilter,
    KICKED,
    MEMBER,
)
from aiogram.types.chat_member_updated import ChatMemberUpdated

from app.src.crud.async_crud.chat_async_crud import chat_async_crud
from app.src.database.database import (
    RedisKeys,
    async_session_maker,
)
from app.src.utils.redis_data import redis_delete

IF_KICKED = ChatMemberUpdatedFilter(member_status_changed=KICKED)
IF_ADDED = ChatMemberUpdatedFilter(member_status_changed=MEMBER)

router: Router = Router()


# TODO. Не работает.
@router.my_chat_member(IF_KICKED)
async def bot_was_kicked(event: ChatMemberUpdated) -> None:
    """
    Обрабатывает событие "бота исключили из чата".
    """
    with async_session_maker() as session:
        chat_async_crud.delete_by_id(
            obj_id=event.chat.id,
            session=session,
        )

    for key in (
        RedisKeys.CHAT_ALL_IDS,
        RedisKeys.CHAT_ALL_TITLES,
    ):
        redis_delete(key=key)

    return

@router.my_chat_member(IF_ADDED)
async def bot_was_added(event: ChatMemberUpdated) -> None:
    """
    Обрабатывает событие "бота добавил в чат".
    """
    async with async_session_maker() as session:
        chat_id_str = str(event.chat.id)
        await chat_async_crud.create(
            obj_data={
                'chat_id': chat_id_str,
                'is_group': (
                    True
                    if chat_id_str.startswith('-')
                    else False
                ),
                'title': event.chat.title,
            },
            session=session,
        )

    for key in (
        RedisKeys.CHAT_ALL_IDS,
        RedisKeys.CHAT_ALL_TITLES,
    ):
        redis_delete(key=key)

    return
