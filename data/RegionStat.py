from data.db_session import SqlAlchemyBase
import sqlalchemy
from data.db_session import *


class RegionStat(SqlAlchemyBase):
    __tablename__ = 'region_stat'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    region_name = sqlalchemy.Column(sqlalchemy.VARCHAR(100))
    members_count = sqlalchemy.Column(sqlalchemy.Integer)
