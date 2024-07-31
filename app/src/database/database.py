"""
Модуль соединения с базой данных через SQLAlchemy.
"""

from typing import AsyncGenerator

from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.src.config.config import settings

DATABASE_ASYNC_URL: str = f'postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.POSTGRES_DB}'
DATABASE_SYNC_URL: str = f'postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.POSTGRES_DB}'


async_engine: AsyncEngine = create_async_engine(
    url=DATABASE_ASYNC_URL,
    echo=settings.DEBUG_DB,
)

async_session_maker: async_sessionmaker = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


sync_engine = create_engine(
    url=DATABASE_SYNC_URL,
    echo=settings.DEBUG_DB,
)

sync_session_maker: sessionmaker = sessionmaker(bind=sync_engine)


class Base(DeclarativeBase):
    """Инициализирует фабрику создания декларативных классов моделей."""


class TableNames:
    """
    Класс представления названий таблиц в базе данных.
    """

    CHAT: str = 'table_chat'
    POLL: str = 'table_poll'


class RedisKeys:
    """Класс представления Redis ключей."""

    PREFIX_SRC: str = 'src_cache_'

    # Chat
    CHAT: str = PREFIX_SRC + 'chat_'
    CHAT_ALL_IDS: str = CHAT + 'all_ids'
    CHAT_ALL_TITLES: str = CHAT + 'all_titles'

    # Poll
    POLL: str = PREFIX_SRC + 'poll_'
    POLL_ALL: str = POLL + 'all'



redis_engine: Redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_CACHE,
    decode_responses=True,
)
