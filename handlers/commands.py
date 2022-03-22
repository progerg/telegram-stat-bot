from aiogram import types
from texts.messages import MESSAGES
from bot import db


async def help_command(message: types.Message):
    await message.answer(MESSAGES['help'])


async def start_bot(message: types.Message):
    user = await db.get_user(message.from_user.id)
    if user:
        await message.answer(MESSAGES['admin']['1'])
    else:
        pass
