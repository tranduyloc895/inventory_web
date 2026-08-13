from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)
settings = get_settings()

# Architecture note: MongoDB is used as an event store/audit log. Its flexible schema 
# is perfect for storing heterogeneous event data (product_created, price_changed) without 
# schema migrations, providing a robust history for tracking and analytics.

_mongo_client: Optional[AsyncIOMotorClient] = None

def get_mongo_db():
    global _mongo_client
    if _mongo_client is None:
        try:
            _mongo_client = AsyncIOMotorClient(
                settings.mongo_url,
                serverSelectionTimeoutMS=5000
            )
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            return None
    return _mongo_client[settings.MONGO_DB]

def close_mongo_client():
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        logger.info("MongoDB connection closed")
