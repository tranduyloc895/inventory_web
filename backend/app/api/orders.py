from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.mysql import get_mysql_session
from app.database.postgres import get_pg_session
from app.schemas.order import OrderListResponse, OrderResponse, OrderCreate
from app.services import order_service
from app.models.user import User
from app.services.auth_service import get_current_user, get_current_admin

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.get("/", response_model=OrderListResponse)
async def list_orders(
    db: AsyncSession = Depends(get_mysql_session),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id if current_user.role != "admin" else None
    return await order_service.get_orders(db, user_id=user_id)

@router.post("/", response_model=OrderResponse)
async def create_order(
    data: OrderCreate, 
    db: AsyncSession = Depends(get_mysql_session),
    pg_db: AsyncSession = Depends(get_pg_session),
    current_user: User = Depends(get_current_user)
):
    return await order_service.create_order(db, pg_db, data, current_user.id)

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_mysql_session),
    current_admin: User = Depends(get_current_admin)
):
    return await order_service.update_order_status(db, order_id, status)

