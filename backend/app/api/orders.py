from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.mysql import get_mysql_session
from app.schemas.order import OrderListResponse, OrderResponse, OrderCreate
from app.services import order_service

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.get("/", response_model=OrderListResponse)
async def list_orders(db: AsyncSession = Depends(get_mysql_session)):
    return await order_service.get_orders(db)

@router.post("/", response_model=OrderResponse)
async def create_order(data: OrderCreate, db: AsyncSession = Depends(get_mysql_session)):
    return await order_service.create_order(db, data)
