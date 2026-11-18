
import os

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy database models."""
    pass


DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username="postgres",
    password=os.getenv("DB_PASSWORD"),
    host="localhost",
    port=5432,
    database="corporate_event_db"
)

# Create the asynchronous database engine.
engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

# Create a session factory for database operations.
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """Provide a database session to FastAPI endpoints."""
    async with SessionLocal() as session:
        yield session
