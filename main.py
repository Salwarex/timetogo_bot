from aiogram import Bot, Dispatcher
from app.handlers import router

import asyncio
import logging
import config

TOKEN_API = config.TOKEN_API

bot = Bot(TOKEN_API)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    if config.DEBUGMODE: logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')