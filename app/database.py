from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import config

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(config.POSTGRES_USER,
                                                                       config.POSTGRES_PASSWORD,
                                                                       config.POSTGRES_HOSTNAME,
                                                                       config.DATABASE_PORT,
                                                                       config.POSTGRES_DB)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)
Base = declarative_base()

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with async_session() as db:
        yield db
