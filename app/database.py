"""
Database configuration for Customer Service
"""
import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from shared.config.settings import settings

# Build asyncpg-compatible URL (strip sslmode which asyncpg doesn't support as URL param)
_db_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
_db_url = re.sub(r'[?&]sslmode=[^&]*', '', _db_url).rstrip('?')

engine = create_async_engine(
    _db_url,
    echo=(settings.environment == "development"),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"ssl": False},
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
