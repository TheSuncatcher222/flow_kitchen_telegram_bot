from celery import Celery

import os
import sys
# INFO: добавляет корневую директорию проекта в sys.path для возможности
#       использования абсолютных путей импорта данных из модулей.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

celery_app: Celery = Celery(
    main='celery_app',
    broker='redis://bot-telegram-redis:6379/1',
    backend='redis://bot-telegram-redis:6379/2',
)

celery_app.autodiscover_tasks(['celery_app.tasks'])

celery_app.conf.timezone = 'Europe/Moscow'

celery_app.conf.beat_schedule = {
    'celery_task_send_pool': {
        'task': 'celery_task_send_pool',
        'schedule': 5.0,
    },
}

