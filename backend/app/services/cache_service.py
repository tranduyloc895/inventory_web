import json
import logging
from typing import Optional, Any
from app.database.redis_client import get_redis

logger = logging.getLogger(__name__)

async def get_cache(key: str) -> Optional[str]:
    redis = get_redis()
    if not redis:
        return None
    
    try:
        data = await redis.get(key)
        return data
    except Exception as e:
        logger.warning(f"Redis get error for key {key}: {e}")
        return None

async def set_cache(key: str, data: Any, ttl: int = 300) -> None:
    redis = get_redis()
    if not redis:
        return
    
    try:
        if isinstance(data, (dict, list)):
            value = json.dumps(data, default=str)
        else:
            value = str(data)
        await redis.setex(key, ttl, value)
    except Exception as e:
        logger.warning(f"Redis set error for key {key}: {e}")

async def delete_cache(key: str) -> None:
    redis = get_redis()
    if not redis:
        return
    
    try:
        await redis.delete(key)
    except Exception as e:
        logger.warning(f"Redis delete error for key {key}: {e}")

async def delete_pattern(pattern: str) -> None:
    redis = get_redis()
    if not redis:
        return
    
    try:
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
    except Exception as e:
        logger.warning(f"Redis delete_pattern error for pattern {pattern}: {e}")
