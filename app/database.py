"""
Database connection and async session management.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from typing import AsyncGenerator

from app.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)

# Base class for all models
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    
    Usage in routes:
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize database tables if they don't already exist."""
    import logging
    logger = logging.getLogger(__name__)
    
    async with engine.begin() as conn:
        try:
            # Check if tables already exist
            result = await conn.execute(text("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'anonymous_users'
                )
            """))
            tables_exist = result.scalar()
            
            if tables_exist:
                logger.info("✅ Database tables already exist")
                return
            
            # Create tables only if they don't exist
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database schema created successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
            # Continue anyway - tables might exist
            pass
