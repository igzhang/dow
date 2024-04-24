from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://devops:1qaz#EDC@db.dev.idadt-tech.com/devops"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600)
async_session_local = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


def row2dict(row):
    """convert Query DB object to dict

    Args:
        row (_type_): _description_

    Returns:
        _type_: _description_
    """
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d
