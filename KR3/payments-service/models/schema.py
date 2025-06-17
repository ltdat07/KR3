from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

def get_sessionmaker(database_url: str):

    engine = create_async_engine(
        database_url,
        echo=False,
        future=True,
    )
    SessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    return SessionLocal, engine
