from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec
from sqlalchemy.orm import sessionmaker


SqlAlchemyBase = dec.declarative_base()

__factory = None


async def global_init(user, password, host, port, dbname):
    global __factory

    if __factory:
        return

    conn_str = f'mysql+aiomysql://{user}:{password}@{host}:{port}/{dbname}?charset=utf8mb4'
    print(f"Подключение к базе данных по адресу {conn_str}")

    engine = create_async_engine(conn_str, pool_pre_ping=True, convert_unicode=True)

    # Создание всех таблиц
    async with engine.begin() as conn:
        # await conn.run_sync(SqlAlchemyBase.metadata.drop_all)
        await conn.run_sync(SqlAlchemyBase.metadata.create_all)

    __factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    from . import __all_models


def create_session() -> AsyncSession:
    global __factory
    return __factory()
