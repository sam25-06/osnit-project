# database.py
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from redis.asyncio import ConnectionPool, Redis

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/intel_dashboard",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/intel_dashboard",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
LIVE_FEED_CHANNEL = "live_threat_feed"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# --- Redis connection pool (foundation for high-frequency cache reads) ---
redis_pool: ConnectionPool = ConnectionPool.from_url(
    REDIS_URL,
    max_connections=50,
    decode_responses=True,
)


def get_redis() -> Redis:
    return Redis(connection_pool=redis_pool)


@asynccontextmanager
async def lifespan_resources():
    """Call on app startup/shutdown to validate connectivity and dispose cleanly."""
    try:
        r = get_redis()
        await r.ping()
        yield
    finally:
        await redis_pool.disconnect()
        await engine.dispose()