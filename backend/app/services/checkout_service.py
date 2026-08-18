import json
from app.database.redis_client import get_redis
from app.schemas.checkout import CheckoutSession
from app.services.cart_service import get_cart, clear_cart
from app.services.order_service import create_order
from app.schemas.order import OrderCreate, OrderItemCreate
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def start_checkout(user_id: int) -> CheckoutSession:
    try:
        redis = await get_redis()
        if not redis:
            raise Exception("Redis not available")
            
        cart = await get_cart(user_id)
        if not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")
            
        session = CheckoutSession(user_id=user_id, cart=cart, status="processing")
        
        # Save session to Redis with 15 minute expiration
        await redis.setex(
            f"checkout:{user_id}",
            900,
            session.model_dump_json()
        )
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Redis Error start_checkout: {str(e)}")
        raise HTTPException(status_code=503, detail="Checkout service unavailable")

async def get_checkout_session(user_id: int) -> CheckoutSession:
    try:
        redis = await get_redis()
        if not redis:
            raise Exception("Redis not available")
            
        data = await redis.get(f"checkout:{user_id}")
        if not data:
            raise HTTPException(status_code=404, detail="No active checkout session")
            
        return CheckoutSession.model_validate_json(data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Redis Error get_checkout: {str(e)}")
        raise HTTPException(status_code=503, detail="Checkout service unavailable")

async def complete_checkout(user_id: int, pg_db, mysql_db) -> dict:
    try:
        session = await get_checkout_session(user_id)
        
        # 1. Create order in PostgreSQL
        order_items = []
        for item in session.cart.items:
            order_items.append(OrderItemCreate(
                product_id=item.product_id,
                quantity=item.quantity
            ))
            
        order_create = OrderCreate(
            items=order_items,
            notes="Order from checkout session"
        )
        
        new_order = await create_order(pg_db, mysql_db, order_create, user_id)
        
        # 2. Clear MongoDB Cart
        await clear_cart(user_id)
        
        # 3. Clear Redis Session
        redis = await get_redis()
        if redis:
            await redis.delete(f"checkout:{user_id}")
            
        return {"message": "Checkout completed successfully", "order_id": new_order.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error complete_checkout: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Checkout failed: {str(e)}")
