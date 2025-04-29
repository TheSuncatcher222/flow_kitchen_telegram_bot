from app.src.crud.chat import chat_crud
from app.src.database.database import (
    RedisKeys,
    async_session_maker,
)
from app.src.models.chat import Chat
from app.src.utils.redis_app import (
    redis_get,
    redis_set,
)

# TODO. Добавить кеш в Redis!


async def get_chat_all_titles() -> list[str]:
    """
    Возвращает список всех названий чатов.
    """
    all_chat_titles: None | dict[list[dict[str, any]]] = redis_get(key=RedisKeys.CHAT_ALL_TITLES)
    if isinstance(all_chat_titles, dict):
        return all_chat_titles['all_chats']

    async with async_session_maker() as session:
        chats: list[Chat | None] = await chat_crud.retrieve_all(session=session)

    if len(chats) == 0:
        redis_set(
            key=RedisKeys.CHAT_ALL_TITLES,
            value={'all_chats': []},
        )

    all_chat_titles: list[str] = [c.title for c in chats]
    redis_set(
        key=RedisKeys.CHAT_ALL_TITLES,
        value={'all_chats': all_chat_titles},
    )

    return all_chat_titles


async def get_chat_id_by_title(title: str) -> int:
    """
    Возвращает ID чата по названию.
    """
    all_chat_ids: dict[str, int] | None = redis_get(key=RedisKeys.CHAT_ALL_IDS)

    if all_chat_ids is None:

        async with async_session_maker() as session:
            chats: list[Chat | None] = await chat_crud.retrieve_all(session=session)
        all_chat_ids: dict[str, int] = {c.title: c.chat_id for c in chats}

        redis_set(
            key=RedisKeys.CHAT_ALL_IDS,
            value=all_chat_ids,
        )

    return all_chat_ids[title]
