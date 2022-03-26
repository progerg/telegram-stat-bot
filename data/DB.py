import datetime
from typing import Optional, Any, List

import aiogram.types
from aiogram import Bot
from sqlalchemy.future import select

from data.Channel import Channel
from data.Member import Member
from data.User import User
from data.db_session import create_session


class DB:
    @staticmethod
    async def get_user(user_id: int) -> User:
        async with create_session() as sess:
            result = await sess.execute(select(User).where(User.user_id == user_id))
            user = result.scalars().first()
        return user

    @staticmethod
    async def get_member(user_id: int, channel_id: int) -> Member:
        async with create_session() as sess:
            result = await sess.execute(select(Member).where(Member.user_id == user_id,
                                                             Member.channel_id == channel_id))
            member = result.scalars().first()
        return member

    @staticmethod
    async def get_channel(channel_id: int) -> Channel:
        async with create_session() as sess:
            result = await sess.execute(select(Channel).where(Channel.user_id == channel_id))
            channel = result.scalars().first()
        return channel

    @staticmethod
    async def get_channels() -> List[Channel]:
        async with create_session() as sess:
            result = await sess.execute(select(Channel))
            channels = result.scalars().all()
        return channels

    @staticmethod
    async def update_channel_members(bot: Bot) -> bool:
        try:
            async with create_session() as sess:
                result = await sess.execute(select(Channel))
                channels = result.scalars().all()
                for channel in channels:
                    count = await bot.get_chat_members_count(channel.channel_id)
                    channel.members_count = count
                    await sess.commit()

            return True
        except:
            return False

    @staticmethod
    async def get_active_members(channel_id: int) -> List[Member]:
        async with create_session() as sess:
            result = await sess.execute(select(Member).where(Member.channel_id == channel_id,
                                                                Member.last_message_day > datetime.date.today() -
                                                                datetime.timedelta(days=30)))
            members = result.scalars().all()
        return members

    @staticmethod
    async def msg_count_up(user: aiogram.types.User, channel_id: int) -> Member:
        async with create_session() as sess:
            result = await sess.execute(select(Member).where(Member.user_id == user.id,
                                                             Member.channel_id == channel_id))
            member = result.scalars().first()
            if member:
                member.msg_count += 1
                member.channel.mes_count += 1
                if member.last_message_day != datetime.date.today():
                    member.last_message_day = datetime.date.today()
            else:
                member = Member()
                member.msg_count = 1
                member.channel_id = channel_id
                member.user_id = user.id
                member.name = user.first_name if 'username' not in user else "@" + user.username
                member.last_message_day = datetime.date.today()
                sess.add(member)
                result = await sess.execute(select(Channel).where(Channel.channel_id == channel_id))
                channel = result.scalars().first()
                channel.mes_count += 1
            await sess.commit()
        return member

    @staticmethod
    async def add_channel(user_id: int, channel_id: int, region_name: str, members_count: int) -> bool:
        async with create_session() as sess:
            result = await sess.execute(select(User).where(User.user_id == user_id))
            user = result.scalars().first()
            if user:
                channel = Channel()
                channel.channel_id = channel_id
                channel.region_name = region_name
                channel.members_count = members_count
                sess.add(channel)
                await sess.commit()

                user.channel_id = channel.id
                await sess.commit()
        return True

    @staticmethod
    async def add_user(user_id: int, username: str = None) -> bool:
        async with create_session() as sess:
            result = await sess.execute(select(User).where(User.user_id == user_id))
            user = result.scalars().first()
            if not user:
                user = User()
                user.user_id = user_id
                user.username = username
                sess.add(user)
                await sess.commit()
                return True
            else:
                return False
