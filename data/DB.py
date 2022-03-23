import datetime
from typing import Optional, Any

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
    async def msg_count_up(user_id: int, channel_id: int) -> Member:
        async with create_session() as sess:
            result = await sess.execute(select(Member).where(Member.user_id == user_id,
                                                             Member.channel_id == channel_id,
                                                             Member.last_message_day > datetime.date.today() -
                                                             datetime.timedelta(days=30)))
            member = result.scalars().first()
            if member:
                member.msg_count += 1
                member.channel.mes_count += 1
            else:
                member = Member()
                member.msg_count = 1
                member.channel_id = channel_id
                member.user_id = user_id
                sess.add()
            member.last_message_day = datetime.date.today()
            await sess.commit()
            return member

    @staticmethod
    async def add_channel(user_id: int, channel_id: int, region_name: str) -> bool:
        async with create_session() as sess:
            result = await sess.execute(select(User).where(User.user_id == user_id))
            user = result.scalars().first()
            if user:
                channel = Channel()
                channel.channel_id = channel_id
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

    @staticmethod
    async def reset() -> bool:
        async with create_session() as sess:
            result = await sess.execute(select(Member))
            members = result.scalars().all()
            for member in members:
                member.msg_count = 0
                member.last_message_day = None
                await sess.commit()
            return True
