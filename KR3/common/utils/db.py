from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import asyncio

from models.schema import Base

def create_db_engine(database_url: str) -> AsyncEngine:

    return create_async_engine(
        database_url,
        echo=False,
        future=True,
    )

async def init_db(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
