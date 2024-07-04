from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.methods.send_poll import SendPoll

from telegram_bot.telegram_bot import dp, bot


@dp.message(CommandStart())
async def handler_command_start(message: Message) -> None:
    await message.answer(text='Привет! Хочешь научиться танцевать? Тогда ты зашел по адресу! https://vk.com/flowkitchen')

@dp.message(Command='/any_text')
async def handler_text(message: Message) -> None:
    await message.answer(text='Я обязательно передам сообщение Шефу, и он вам ответит.')