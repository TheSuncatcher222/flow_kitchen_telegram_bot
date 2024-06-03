import asyncio
import logging

from telegram_bot.commands import bot, dp

async def main():
    bot_task = asyncio.create_task(dp.start_polling(bot))
    await asyncio.gather(bot_task,)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
