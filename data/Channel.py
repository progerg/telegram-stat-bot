from data.db_session import SqlAlchemyBase
import sqlalchemy
from data.db_session import *


class Channel(SqlAlchemyBase):
    __tablename__ = 'channels'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    channel_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    user = orm.relationship('User', back_populates='channel', lazy='selectin')
