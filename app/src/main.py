import asyncio
import logging
import os
import sys

# INFO: добавляет корневую директорию проекта в sys.path для возможности
#       использования абсолютных путей импорта данных из модулей.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.src.telegram_bot.bot import bot
from app.src.telegram_bot.dispatcher import dp


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
