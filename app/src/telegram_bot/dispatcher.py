from aiogram import (
    Dispatcher,
    Router,
)
from aiogram.fsm.storage.memory import MemoryStorage

from app.src.telegram_bot.routers.poll import router as poll_router
from app.src.telegram_bot.routers.test import router as test_router

dp: Dispatcher = Dispatcher(
    storage=MemoryStorage(),
)

routers: list[Router] = (
    poll_router,
    test_router,
)
for router in routers:
    dp.include_router(router)
