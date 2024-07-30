from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

DIR_SRC: Path = Path(__file__).parent.parent

NL: str = '\n'


class Settings(BaseSettings):
    """Класс представления переменных окружения."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="UTF-8",
        extra="allow",
    )

    """Настройки базы данных PostgreSQL."""
    DB_HOST: str = 'postgresql'
    DB_PORT: int = 5432
    POSTGRES_DB: str = 'db_name'
    POSTGRES_PASSWORD: str = 'db_pass'
    POSTGRES_USER: str = 'db_user'

    """Настройки базы данных Redis."""
    REDIS_HOST: str = 'redis'
    REDIS_PORT: int = 6379
    REDIS_DB_CELERY_BACKEND: int = 0
    REDIS_DB_CELERY_BROKER: int = 1
    REDIS_DB_CACHE: int = 2

    """Настройки SQLAlchemy Admin."""
    ADMIN_USERNAME: str = 'admin'
    ADMIN_PASSWORD: str = 'admin'
    ADMIN_SECRET_KEY: str = 'string'

    """Настройки Telegram Bot."""
    BOT_ADMIN_IDS: str
    BOT_TOKEN: str
    DEBUG_DB: bool = True


settings = Settings()


class TimeIntervals:
    """Класс представления таймаутов."""

    # Seconds.

    SECONDS_IN_1_MINUTE: int = 60
    SECONDS_IN_1_HOUR: int = SECONDS_IN_1_MINUTE * 60
    SECONDS_IN_1_DAY: int = SECONDS_IN_1_HOUR * 24
