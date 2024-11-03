import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message


bot=Bot(token="TOKEN")
dp=Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Доброго дня {message.from_user.full_name}! Хорошей погоды!")

async def main():
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
