from fastapi import APIRouter, Depends
from app.schemas.cart import Cart, AddToCartRequest
from app.services import cart_service, product_service
from app.models.user import User
from app.services.auth_service import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.mysql import get_mysql_session

router = APIRouter(prefix="/api/cart", tags=["cart"])

@router.get("/", response_model=Cart)
async def get_my_cart(current_user: User = Depends(get_current_user)):
    return await cart_service.get_cart(current_user.id)

@router.post("/add", response_model=Cart)
async def add_item_to_cart(
    req: AddToCartRequest,
    current_user: User = Depends(get_current_user),
    mysql_db: AsyncSession = Depends(get_mysql_session)
):
    # Lookup product to get name and price
    product = await product_service.get_product(mysql_db, req.product_id)
    return await cart_service.add_item_to_cart(
        user_id=current_user.id,
        product_id=req.product_id,
        product_name=product["name"],
        quantity=req.quantity,
        unit_price=product["price"]
    )

@router.delete("/")
async def clear_my_cart(current_user: User = Depends(get_current_user)):
    await cart_service.clear_cart(current_user.id)
    return {"message": "Cart cleared"}
