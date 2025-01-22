import asyncio
from aiogram import Bot, Dispatcher

from config import MY_TOKEN_BOT
from handlers import router

bot = Bot(token=MY_TOKEN_BOT)
dp = Dispatcher()
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())