from typing import Optional

from sqlalchemy.future import select

from data.Channel import Channel
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
    async def get_channel(channel_id: int) -> Channel:
        async with create_session() as sess:
            result = await sess.execute(select(Channel).where(Channel.user_id == channel_id))
            channel = result.scalars().first()
        return channel
