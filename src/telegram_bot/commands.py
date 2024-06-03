from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.methods.send_poll import SendPoll

from telegram_bot.telegram_bot import dp, bot
 

@dp.message(CommandStart())
async def handler_command_start(message: Message) -> None:    
    await message.answer(text='Когда придешь на занятие? =)')
