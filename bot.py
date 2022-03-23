import asyncio
import logging
from aiogram import types

import aioschedule
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ChatType
from aiogram.utils import executor

from config import *
from data.DB import DB
from data.db_session import global_init
from texts.messages import MESSAGES

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

db = DB()
logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    username = message.from_user.username if 'username' in message.from_user else None
    answer = await db.add_user(user_id=message.from_user.id, username=username)
    if answer:
        await message.answer(MESSAGES['bot']['1'])
    else:
        await message.answer(MESSAGES['bot']['2'])


@dp.message_handler(chat_type=[ChatType.GROUP, ChatType.SUPERGROUP], commands=['add_bot'])
async def add_bot(message: types.Message):
    try:
        region = " ".join(message.text.split()[1:])
    except:
        await message.answer(MESSAGES['admin']['2'])
        return
    if region:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member['status'] == 'administrator' or member['status'] == 'creator':
            await db.add_channel(message.from_user.id, message.chat.id)
            await message.answer(MESSAGES['admin']['1'])


@dp.message_handler(chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def chat_message_handler(message: types.Message):
    await db.msg_count_up(message.from_user.id, message.chat.id)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


async def scheduler():
    aioschedule.every(5).minutes.do(db.reset())
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def startup_(_):
    await global_init(user=DB_LOGIN, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME)
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown, on_startup=startup_)
