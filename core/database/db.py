from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.settings import settings
from core.database.base import Base

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession: # type: ignore
    async with AsyncSessionLocal() as session:
        yield session
async def init_database() -> None:
    """Create database tables."""

    async with engine.begin() as connection:
        await connection.run_sync(
            Base.metadata.create_all
        )