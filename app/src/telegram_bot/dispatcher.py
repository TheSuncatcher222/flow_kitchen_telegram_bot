from aiogram import (
    Dispatcher,
    Router,
)
from aiogram.fsm.storage.memory import MemoryStorage

from app.src.telegram_bot.routers.add_poll import router as add_poll_router
from app.src.telegram_bot.routers.chat_control import router as chat_control_router
from app.src.telegram_bot.routers.my_polls import router as my_polls_router
from app.src.telegram_bot.routers.start import router as start_router

dp: Dispatcher = Dispatcher(
    storage=MemoryStorage(),
)

routers: list[Router] = (
    add_poll_router,
    chat_control_router,
    my_polls_router,
    start_router,
)
for router in routers:
    dp.include_router(router)
