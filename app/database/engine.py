from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_size=10,
        max_overflow=20
        )

async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
        )

class Base(DeclarativeBase):
    pass

async def get_db():
    """
    FastPI Dependency: Yields a database session 
    to a route and ensures it's closed afterward.
    """

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
