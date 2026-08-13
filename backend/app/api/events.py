from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.event_service import get_product_events

router = APIRouter(tags=["events"])

@router.get("/api/products/{id}/events", response_model=List[Dict[str, Any]])
async def list_product_events(id: int):
    events = await get_product_events(id)
    return events
