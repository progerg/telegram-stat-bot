from data.db_session import SqlAlchemyBase
import sqlalchemy
from data.db_session import *


class Reset(SqlAlchemyBase):
    __tablename__ = 'reset'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    next_reset = sqlalchemy.Column(sqlalchemy.DateTime)
