from datetime import datetime, timezone
import logging
from typing import Dict, Any, List
from app.database.mongodb import get_mongo_db

logger = logging.getLogger(__name__)

async def log_event(product_id: int, event_type: str, metadata: Dict[str, Any] = None) -> None:
    db = get_mongo_db()
    if db is None:
        logger.warning("MongoDB not available, skipping event logging.")
        return
    
    try:
        collection = db["product_events"]
        event_doc = {
            "product_id": product_id,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc),
            "metadata": metadata or {}
        }
        await collection.insert_one(event_doc)
    except Exception as e:
        logger.warning(f"Failed to log event to MongoDB: {e}")

async def get_product_events(product_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    db = get_mongo_db()
    if db is None:
        logger.warning("MongoDB not available, returning empty events list.")
        return []
    
    try:
        collection = db["product_events"]
        cursor = collection.find({"product_id": product_id}).sort("timestamp", -1).limit(limit)
        events = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])  # convert ObjectId to string
            events.append(doc)
        return events
    except Exception as e:
        logger.warning(f"Failed to fetch events from MongoDB: {e}")
        return []
