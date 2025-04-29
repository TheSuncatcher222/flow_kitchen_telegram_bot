from aiogram import (
    Dispatcher,
    Router,
)
from aiogram.fsm.storage.memory import MemoryStorage

from app.src.telegram_bot.routers.chat_control import router as chat_control
from app.src.telegram_bot.routers.course_add import router as course_add
from app.src.telegram_bot.routers.course_main import router as course_main
from app.src.telegram_bot.routers.course_my import router as course_my
from app.src.telegram_bot.routers.fallback import router as _fallback
from app.src.telegram_bot.routers.poll_add import router as poll_add
from app.src.telegram_bot.routers.poll_my import router as poll_my
from app.src.telegram_bot.routers.redis_clear import router as redis_clear
from app.src.telegram_bot.routers.start import router as start

dp: Dispatcher = Dispatcher(
    storage=MemoryStorage(),
)

routers: list[Router] = (
    chat_control,
    course_add,
    course_my,
    poll_add,
    course_main,
    poll_my,
    redis_clear,
    start,
    # WARNING! Роутер _fallback должен быть зарегистрирован ниже всех остальных!
    _fallback,
)
for router in routers:
    dp.include_router(router)
