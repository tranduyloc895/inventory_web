import redis.asyncio as redis
from app.config import get_settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)
settings = get_settings()

# Architecture note: Redis is used as an in-memory caching layer to offload read requests 
# from PostgreSQL. It provides fast access to frequently read product lists and details, 
# significantly improving API response times and reducing database load.

_redis_client: Optional[redis.Redis] = None

async def init_redis():
    global _redis_client
    try:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_timeout=2.0
        )
        # Test connection
        await _redis_client.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.warning(f"Could not connect to Redis: {e}. Caching will be disabled.")
        _redis_client = None

async def close_redis():
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis connection closed")

def get_redis() -> Optional[redis.Redis]:
    return _redis_client
