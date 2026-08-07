"""
Database configuration.

Provides:

- Async SQLAlchemy Engine
- Async Session Factory
- Dependency for FastAPI
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.app.core.config import settings


DATABASE_URL = settings.DATABASE_URL

# Convert SQLite sync URL -> async URL
if DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = DATABASE_URL.replace(
        "sqlite:///",
        "sqlite+aiosqlite:///",
        1,
    )

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency.

    Returns:
        Async database session.
    """
    async with AsyncSessionLocal() as session:
        yield session