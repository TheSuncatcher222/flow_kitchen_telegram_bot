"""
Модуль с вспомогательными функциями для извлечения и сохранения данных в Redis.

Использование хранилища Redis для ручного извлечения и сохранения данных
осуществляется через функции redis_get и redis_set соответственно.
"""

import json

from app.src.database.database import redis_engine


def redis_delete(key: str) -> None:
    """
    Удаляет данные из Redis по указанному ключу.
    """
    redis_engine.delete(key)
    return


def redis_get(key: str) -> any:
    """
    Извлекает данные из Redis по указанному ключу
    в типах данных Python.
    """
    data: any = redis_engine.get(name=key)
    if data is None:
        return None
    try:
        return json.loads(s=data)
    except json.JSONDecodeError:
        return data


def redis_set(key: str, value: any, ex_sec: int = 10) -> None:
    """
    Сохраняет данные в Redis по указанному ключу.

    Преобразует тип данных dict в JSON.
    """
    if isinstance(value, dict):
        value = json.dumps(value)

    redis_engine.set(
        name=key,
        value=value,
        ex=ex_sec,
    )
    return
