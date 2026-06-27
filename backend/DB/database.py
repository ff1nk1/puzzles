from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from backend.core.config import settings
#ВСПОМНИТЬ ЕСЛИ ЧО
#alembic revision --autogenerate -m 'initial'
#alembic upgrade head

engine = create_async_engine(settings.ASYNC_DATABASE_URL)  # создали движок БД
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)  # передали наш движок в создатель сессий

async def connect_to_db():
    async with async_session_maker() as session:
        yield session

class Base(DeclarativeBase):
    pass
