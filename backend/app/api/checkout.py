from fastapi import APIRouter, Depends
from app.schemas.checkout import CheckoutSession
from app.services import checkout_service
from app.models.user import User
from app.services.auth_service import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres import get_pg_session
from app.database.mysql import get_mysql_session

router = APIRouter(prefix="/api/checkout", tags=["checkout"])

@router.post("/start", response_model=CheckoutSession)
async def start_checkout(current_user: User = Depends(get_current_user)):
    return await checkout_service.start_checkout(current_user.id)

@router.get("/session", response_model=CheckoutSession)
async def get_checkout_session(current_user: User = Depends(get_current_user)):
    return await checkout_service.get_checkout_session(current_user.id)

@router.post("/complete")
async def complete_checkout(
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_session),
    mysql_db: AsyncSession = Depends(get_mysql_session)
):
    return await checkout_service.complete_checkout(current_user.id, pg_db, mysql_db)
