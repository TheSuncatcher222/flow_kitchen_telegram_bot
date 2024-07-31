from sqlalchemy.sql import select
from sqlalchemy.sql.selectable import Select

from app.src.database.database import (
    RedisKeys,
    sync_session_maker,
)
from app.src.models.chat import Chat
from app.src.utils.redis_data import (
    redis_get,
    redis_set,
)

# TODO. Рефакторинг!


def get_chat_all_titles() -> list[str]:
    """
    Возвращает список всех названий чатов.
    """
    all_chat_titles: None | dict[list[dict[str, any]]] = redis_get(key=RedisKeys.CHAT_ALL_TITLES)
    if isinstance(all_chat_titles, dict):
        return all_chat_titles['all_chats']

    with sync_session_maker() as session:
        query: Select = select(Chat)
        queryset: list[Chat] = (session.execute(query)).scalars().all()

    if len(queryset) == 0:
        redis_set(
            key=RedisKeys.CHAT_ALL_TITLES,
            value={'all_chats': []},
        )

    all_chat_titles: list[str] = [chat.title for chat in queryset]
    redis_set(
        key=RedisKeys.CHAT_ALL_TITLES,
        value={'all_chats': all_chat_titles},
    )

    return all_chat_titles


def get_chat_id_by_title(title: str) -> int:
    """
    Возвращает ID чата по названию.
    """
    all_chat_ids: dict[str, int] | None = redis_get(key=RedisKeys.CHAT_ALL_IDS)

    if all_chat_ids is None:

        with sync_session_maker() as session:
            query: Select = select(Chat)
            queryset: list[Chat] = (session.execute(query)).scalars().all()

        all_chat_ids: dict[str, int] = {}
        for chat in queryset:
            all_chat_ids[chat.title] = chat.chat_id

        redis_set(
            key=RedisKeys.CHAT_ALL_IDS,
            value=all_chat_ids,
        )

    return all_chat_ids[title]


def get_chat_title_by_id(id: int) -> str:
    """
    Возвращает ID чата по названию.
    """
    all_chat_ids: dict[str, int] | None = redis_get(key=RedisKeys.CHAT_ALL_IDS)

    if all_chat_ids is None:

        with sync_session_maker() as session:
            query: Select = select(Chat)
            queryset: list[Chat] = (session.execute(query)).scalars().all()

        all_chat_ids: dict[str, int] = {}
        for chat in queryset:
            all_chat_ids[chat.title] = chat.chat_id

        redis_set(
            key=RedisKeys.CHAT_ALL_IDS,
            value=all_chat_ids,
        )

    return all_chat_ids[id]
