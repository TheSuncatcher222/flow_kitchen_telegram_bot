"""
Модуль соединения с базой данных через SQLAlchemy.
"""

from typing import AsyncGenerator

from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
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

sync_engine = create_engine(
    DATABASE_SYNC_URL,
    echo=settings.DEBUG_DB,
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


class Base(DeclarativeBase):
    """Инициализирует фабрику создания декларативных классов моделей."""


class TableNames:
    """
    Класс представления названий таблиц в базе данных.
    """

    chat: str = 'table_chat'
    course: str = 'table_course'
    poll: str = 'table_poll'
    tariff: str = 'table_tariff'
    user: str = 'table_user'


class RedisKeys:
    """Класс представления Redis ключей."""

    __PREFIX_SRC: str = 'src_cache_'

    # Chat
    __CHAT: str = __PREFIX_SRC + 'chat_'
    CHAT_ALL_IDS: str = __CHAT + 'all_ids'
    CHAT_ALL_TITLES: str = __CHAT + 'all_titles'

    # Poll
    __POLL: str = __PREFIX_SRC + 'poll_'
    POLL_ALL: str = __POLL + 'all'



redis_engine: Redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB_CACHE,
    decode_responses=True,
)
