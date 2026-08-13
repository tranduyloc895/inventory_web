from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Architecture note: MySQL is used for the orders domain. Using a separate relational database 
# allows us to decouple the high-volume transaction processing (orders) from the core catalog (products).
# This is a common pattern in microservices to scale domains independently.

engine = create_async_engine(
    settings.mysql_url,
    echo=False,
    future=True,
    pool_pre_ping=False
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_mysql_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"MySQL session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
