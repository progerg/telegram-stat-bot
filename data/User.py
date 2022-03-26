from data.db_session import SqlAlchemyBase
import sqlalchemy
from data.db_session import *


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.BigInteger, unique=True)
    username = sqlalchemy.Column(sqlalchemy.VARCHAR(128), unique=True, default=None)
    channel_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('channels.id'), unique=True)
    channel = orm.relationship("Channel", back_populates='user', lazy='selectin')
