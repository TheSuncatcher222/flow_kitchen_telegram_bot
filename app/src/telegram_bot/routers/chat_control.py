from aiogram import Router
from aiogram.filters import (
    ChatMemberUpdatedFilter,
    KICKED,
    LEFT,
    MEMBER,
)
from aiogram.types.chat_member_updated import ChatMemberUpdated

from app.src.crud.chat import chat_crud
from app.src.database.database import (
    RedisKeys,
    async_session_maker,
)
from app.src.utils.redis_app import redis_delete

IF_ADDED: ChatMemberUpdatedFilter = ChatMemberUpdatedFilter(member_status_changed=MEMBER)
IF_KICKED: ChatMemberUpdatedFilter = ChatMemberUpdatedFilter(member_status_changed=KICKED)
IF_LEFT: ChatMemberUpdatedFilter = ChatMemberUpdatedFilter(member_status_changed=LEFT)

router: Router = Router()


@router.my_chat_member(IF_ADDED)
async def bot_was_added(event: ChatMemberUpdated) -> None:
    """
    Обрабатывает событие "бота добавил в чат".
    """
    async with async_session_maker() as session:
        chat_id_str: str = str(event.chat.id)
        try:
            await chat_crud.create(
                obj_data={
                    'chat_id': chat_id_str,
                    'is_group': chat_id_str.startswith('-'),
                    'title': event.chat.title,
                },
                session=session,
            )
        except ValueError as err:
            if chat_crud.unique_columns_err != err.args[0]:
                raise
            return

    for key in (
        RedisKeys.CHAT_ALL_IDS,
        RedisKeys.CHAT_ALL_TITLES,
    ):
        redis_delete(key=key)


@router.my_chat_member(IF_KICKED)
@router.my_chat_member(IF_LEFT)
async def bot_was_removed(event: ChatMemberUpdated) -> None:
    """
    Обрабатывает событие "бота исключили/забанили из чата".
    """
    async with async_session_maker() as session:
        await chat_crud.delete_by_chat_id(
            chat_id=str(event.chat.id),
            session=session,
        )

    for key in (
        RedisKeys.CHAT_ALL_IDS,
        RedisKeys.CHAT_ALL_TITLES,
    ):
        redis_delete(key=key)
