import asyncio
import logging

import aioschedule
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

from config import *
from data.DB import DB
from data.db_session import global_init
from handlers.register_handlers import register_handlers_common

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

db = DB()
logging.basicConfig(level=logging.INFO)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


async def scheduler():
    # aioschedule.every(5).minutes.do(mail)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def startup_(_):
    await register_handlers_common(dp)
    await global_init(user=DB_LOGIN, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME)
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown, on_startup=startup_)
