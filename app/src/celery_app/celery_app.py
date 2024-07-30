import os
import sys

from celery import Celery
from celery.schedules import crontab

# INFO: добавляет корневую директорию проекта в sys.path для возможности
#       использования абсолютных путей импорта данных из модулей.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.src.config.config import (
    TimeIntervals,
    settings,
)

celery_app: Celery = Celery(
    main='celery_app',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB_CELERY_BROKER}',
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB_CELERY_BACKEND}',
)

celery_app.autodiscover_tasks(
    [
        'src.celery_app.poll',
    ],
)

celery_app.conf.beat_schedule = {
    'send_polls': {
        'task': 'src.celery_app.poll.tasks.send_polls',
        'schedule': TimeIntervals.SECONDS_IN_1_MINUTE,
    },
}

celery_app.conf.update(
    enable_utc=True,
    result_expires=TimeIntervals.SECONDS_IN_1_DAY,
    timezone='UTC',
)


class CeleryPriority:
    """
    Класс с приоритетами задач Celery.
    """

    NONE: int = 9
    VERY_LOW: int = 8
    LOW: int = 7
    MEDIUM: int = 5
    HIGH: int = 3
    VERY_HIGH: int = 2
    IMPORTANT: int = 1
    MOST_IMPORTANT: int = 0


class CeleryTasksPriority:
    """
    Класс связи задач Celery и их приоритетов.
    """

    POOL_SEND_POLLS = CeleryPriority.MEDIUM
