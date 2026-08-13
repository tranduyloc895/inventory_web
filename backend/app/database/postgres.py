from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Architecture note: PostgreSQL is used as the primary relational store for core product, category, 
# and supplier data. It provides strong ACID guarantees, robust relational integrity, and advanced 
# querying capabilities suitable for master data management.

engine = create_async_engine(
    settings.postgres_url,
    echo=False,
    future=True,
    pool_pre_ping=True
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_pg_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"PostgreSQL session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
