from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import asyncio

# Импортируем metadata моделей из сервиса через относительный импорт
# Здесь предполагается, что в корне /app лежит папка models/ с вашим schema.py
from models.schema import Base  # для Orders Service: models/schema.py
# Для Payments Service сделайте аналогичный импорт в его own db.py,
# либо используйте общий Base, если модели лежат там же.

def create_db_engine(database_url: str) -> AsyncEngine:
    """
    Создаёт асинхронный SQLAlchemy-движок.
    """
    # убрали pool_pre_ping, чтобы не выходило ошибок с разными event-loop в тестах
    return create_async_engine(
        database_url,
        echo=False,
        future=True,
    )

async def init_db(engine: AsyncEngine):
    """
    При запуске приложения вызывает Base.metadata.create_all(),
    чтобы в БД были созданы все таблицы по описанным моделям.
    """
    async with engine.begin() as conn:  # type: AsyncConnection
        await conn.run_sync(Base.metadata.create_all)
