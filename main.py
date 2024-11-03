import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import TOKEN

import random

bot=Bot(token=TOKEN)
dp=Dispatcher()

@dp.message(F.photo)
async def help(message: Message):
    await message.answer('"то"')


@dp.message(F.text == 'Что такое ИИ?')
async def help(message: Message):
    await message.answer('Искуственный интеллект')


@dp.message(Command('help'))
async def help(message: Message):
    await message.answer('Этот бот умеет выполнять команды: \n/start - запуск бота\n /help - помощь\n /weather - погода')

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Доброго дня {message.from_user.full_name}! Хорошей погоды!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
