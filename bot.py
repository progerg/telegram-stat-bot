import asyncio
import logging
from typing import List

import aiohttp
from aiogram import types

import aioschedule
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ChatType
from aiogram.utils import executor
from sqlalchemy.future import select

from channel_url import CHANNEL_TO_URL

from config import *
from data.Channel import Channel
from data.DB import DB
from data.RegionStat import RegionStat
from data.db_session import global_init, create_session
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


@dp.message_handler(commands=['mail'])
async def mail_command(message: types.Message):
    if message.from_user.id in ADMINS:
        text = message.text[5:]
        if text:
            channels = await db.get_channels()
            for channel in channels:
                try:
                    await bot.send_message(chat_id=channel.channel_id, text=text)
                except:
                    await message.answer(MESSAGES['bot']['3'].replace('{region}', channel.region_name))


@dp.message_handler(commands=['top'])
async def top_command(message: types.Message):
    channels = await db.get_channels()
    msg = 'Топ по количеству участников:\n'
    channels.sort(key=lambda x: x.members_count, reverse=True)
    for n, channel in enumerate(channels):
        msg += f'{n + 1}. {channel.region_name} - {channel.members_count}'
    await message.answer(msg)


@dp.message_handler(chat_type=[ChatType.GROUP, ChatType.SUPERGROUP], commands=['add_bot'])
async def add_bot(message: types.Message):
    user = await db.get_user(message.from_user.id)
    if user:
        try:
            region = " ".join(message.text.split()[1:])
        except:
            await message.answer(MESSAGES['admin']['2'])
            return
        if region:
            member = await bot.get_chat_member(message.chat.id, message.from_user.id)
            members_count = await bot.get_chat_members_count(message.chat.id)
            if member['status'] == 'administrator' or member['status'] == 'creator':
                await db.add_channel(message.from_user.id, message.chat.id, region, members_count)
                await message.answer(MESSAGES['admin']['1'])
        else:
            await message.answer(MESSAGES['admin']['2'])
    else:
        await message.answer(MESSAGES['admin']['4'])


async def get_inline_query_results(items_list: List[Channel]) -> List[types.InlineQueryResultArticle]:
    results = []
    for item in items_list:
        members = await db.get_active_members(channel_id=item.channel_id)
        best_member = sorted(members, key=lambda member: member.msg_count, reverse=True)
        stat_text = MESSAGES['admin']['3'].replace('{region}', item.region_name)\
            .replace('{active}', str(len(members)))\
            .replace('{msg_count}', str(item.mes_count))

        for n, member_ in enumerate(best_member[:5]):
            stat_text += f'{n + 1}. {member_.name} - {member_.msg_count}\n'

        results.append(types.InlineQueryResultArticle(
            id=str(item.id),
            title=item.region_name,
            input_message_content=types.InputTextMessageContent(
                message_text=stat_text,
                disable_web_page_preview=True
            )
        )
        )
    return results


@dp.inline_handler()
async def empty_query(query: types.InlineQuery):
    regions_list = await db.get_channels()
    results = await get_inline_query_results(regions_list)
    await query.answer(results=results, cache_time=20)


@dp.message_handler(chat_type=[ChatType.GROUP, ChatType.SUPERGROUP])
async def chat_message_handler(message: types.Message):
    await db.msg_count_up(message.from_user, message.chat.id)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


async def get_regions_stats():
    for region, url in CHANNEL_TO_URL.items():
        async with create_session as sess:
            result = await sess.execute(select(RegionStat).where(RegionStat.region_name == region))
            region_stat = result.scalars().first()

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    html = html.split('<div class="tgme_page_extra">')[1]
                    data = html.split('</div>')[0]
                    member_count = data.split('members')[0][:-1]
            region_stat.members_count = member_count
            await sess.commit()


async def scheduler():
    aioschedule.every(60).minutes.do(db.update_channel_members(bot))
    aioschedule.every(6).hours.do(get_regions_stats())
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def startup_(_):
    await global_init(user=DB_LOGIN, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, dbname=DB_NAME)
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown, on_startup=startup_)
