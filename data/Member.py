from data.db_session import SqlAlchemyBase
import sqlalchemy
from data.db_session import *


class Member(SqlAlchemyBase):
    __tablename__ = 'members'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.BigInteger, unique=True)
    msg_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    channel_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('channels.id'))
    channel = orm.relationship('Channel', back_populates='members', lazy='selectin')
    last_message_day = sqlalchemy.Column(sqlalchemy.Date)
