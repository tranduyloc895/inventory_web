from app.database.mongodb import get_mongo_db
from app.schemas.cart import Cart, CartItem
from fastapi import HTTPException
import traceback
import logging

logger = logging.getLogger(__name__)

async def get_cart(user_id: int) -> Cart:
    try:
        db = get_mongo_db()
        if db is None:
            raise Exception("MongoDB not initialized")
            
        collection = db.carts
        cart_doc = await collection.find_one({"user_id": user_id})
        
        if cart_doc:
            return Cart(**cart_doc)
        return Cart(user_id=user_id)
    except Exception as e:
        logger.error(f"MongoDB Error get_cart: {str(e)}")
        raise HTTPException(status_code=503, detail="Cart service unavailable")

async def add_item_to_cart(user_id: int, product_id: int, product_name: str, quantity: int, unit_price: float) -> Cart:
    try:
        db = get_mongo_db()
        if db is None:
            raise Exception("MongoDB not initialized")
            
        collection = db.carts
        cart = await get_cart(user_id)
        
        # Check if item exists
        item_found = False
        for item in cart.items:
            if item.product_id == product_id:
                item.quantity += quantity
                item_found = True
                break
                
        if not item_found:
            cart.items.append(CartItem(
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price
            ))
            
        # Recalculate total
        cart.total_amount = sum(item.quantity * item.unit_price for item in cart.items)
        
        # Save to DB
        await collection.update_one(
            {"user_id": user_id},
            {"$set": cart.model_dump()},
            upsert=True
        )
        return cart
    except Exception as e:
        logger.error(f"MongoDB Error add_item_to_cart: {str(e)}")
        raise HTTPException(status_code=503, detail="Cart service unavailable")

async def clear_cart(user_id: int) -> bool:
    try:
        db = get_mongo_db()
        if db is None:
            raise Exception("MongoDB not initialized")
            
        collection = db.carts
        await collection.delete_one({"user_id": user_id})
        return True
    except Exception as e:
        logger.error(f"MongoDB Error clear_cart: {str(e)}")
        return False
