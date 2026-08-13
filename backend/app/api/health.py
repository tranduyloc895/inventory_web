from fastapi import APIRouter, Response
from app.database.postgres import engine as pg_engine
from app.database.mysql import engine as mysql_engine
from app.database.mongodb import get_mongo_db
from app.database.redis_client import get_redis
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/ready")
async def readiness_check(response: Response):
    status = {
        "postgres": "down",
        "mysql": "down",
        "mongodb": "down",
        "redis": "down"
    }
    
    # Check Postgres
    try:
        async with pg_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            status["postgres"] = "up"
    except Exception as e:
        logger.error(f"Postgres health check failed: {e}")

    # Check MySQL
    try:
        async with mysql_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            status["mysql"] = "up"
    except Exception as e:
        logger.error(f"MySQL health check failed: {e}")

    # Check MongoDB
    try:
        db = get_mongo_db()
        if db is not None:
            await db.command("ping")
            status["mongodb"] = "up"
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        
    # Check Redis
    try:
        redis = get_redis()
        if redis is not None:
            await redis.ping()
            status["redis"] = "up"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        
    is_ready = all(v == "up" for v in status.values())
    if not is_ready:
        response.status_code = 503
        
    return {"status": status, "ready": is_ready}
