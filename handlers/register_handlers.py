from aiogram import Dispatcher

from handlers.commands import *


async def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(help_command, commands='help', state='*')
    dp.register_message_handler(start_bot, commands='start', state='*')