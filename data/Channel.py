from data.db_session import SqlAlchemyBase
import sqlalchemy
from data.db_session import *


class Channel(SqlAlchemyBase):
    __tablename__ = 'channels'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    members_count = sqlalchemy.Column(sqlalchemy.Integer)
    members = orm.relationship('Member', back_populates='channel', lazy='selectin')
    region_name = sqlalchemy.Column(sqlalchemy.VARCHAR(50))
    channel_id = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    mes_count = sqlalchemy.Column(sqlalchemy.BigInteger, default=0)
    user = orm.relationship('User', back_populates='channel', lazy='selectin')
