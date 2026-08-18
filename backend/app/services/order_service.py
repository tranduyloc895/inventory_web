from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from fastapi import HTTPException
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate
from app.services.product_service import get_product

async def get_orders(db: AsyncSession, mysql_db: AsyncSession, user_id: int = None) -> dict:
    stmt = select(Order).options(joinedload(Order.items)).order_by(Order.created_at.desc())
    if user_id is not None:
        from app.models.product import Product
        from sqlalchemy import or_
        
        # Get products owned by this user
        product_stmt = select(Product.id).where(Product.owner_id == user_id)
        product_result = await mysql_db.execute(product_stmt)
        owned_product_ids = product_result.scalars().all()
        
        if owned_product_ids:
            stmt = stmt.where(
                or_(
                    Order.user_id == user_id,
                    Order.items.any(OrderItem.product_id.in_(owned_product_ids))
                )
            )
        else:
            stmt = stmt.where(Order.user_id == user_id)
            
    result = await db.execute(stmt)
    orders = result.unique().scalars().all()
    
    # Dynamically set can_process attribute for frontend UX
    for order in orders:
        if user_id is None:
            order.can_process = True
        else:
            order.can_process = any(item.product_id in (owned_product_ids if 'owned_product_ids' in locals() else []) for item in order.items)
            
    return {"items": orders, "total": len(orders)}

async def create_order(db: AsyncSession, mysql_db: AsyncSession, data: OrderCreate, user_id: int) -> Order:
    new_order = Order(notes=data.notes, status="pending", user_id=user_id)
    db.add(new_order)
    await db.flush() # get new_order.id
    
    total_amount = 0.0
    for item_data in data.items:
        # BUG FIX: Fetch real product from MySQL to get authentic price and name
        real_product = await get_product(mysql_db, item_data.product_id)
        if not real_product:
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
            
        authentic_price = real_product["price"]
        authentic_name = real_product["name"]
        
        subtotal = item_data.quantity * authentic_price
        total_amount += subtotal
        
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data.product_id,
            product_name=authentic_name,
            quantity=item_data.quantity,
            unit_price=authentic_price,
            subtotal=subtotal
        )
        db.add(order_item)
        
    new_order.total_amount = total_amount
    await db.commit()
    
    # Refresh and load items
    stmt = select(Order).options(joinedload(Order.items)).where(Order.id == new_order.id)
    result = await db.execute(stmt)
    return result.unique().scalars().first()

async def update_order_status(db: AsyncSession, mysql_db: AsyncSession, order_id: int, status: str, current_user) -> Order:
    stmt = select(Order).options(joinedload(Order.items)).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.unique().scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # Check if the current user is the owner of any product in this order
    product_ids = [item.product_id for item in order.items]
    if product_ids:
        from app.models.product import Product
        product_stmt = select(Product.owner_id).where(Product.id.in_(product_ids))
        product_result = await mysql_db.execute(product_stmt)
        owner_ids = product_result.scalars().all()
        
        if current_user.role != "admin" and current_user.id not in owner_ids:
            raise HTTPException(status_code=403, detail="Not authorized to update this order: You do not own the products in this order.")
    if status == "completed" and order.status != "completed":
        from app.models.product import Product
        from app.services.cache_service import delete_cache
        for item in order.items:
            stmt_prod = select(Product).where(Product.id == item.product_id)
            res_prod = await mysql_db.execute(stmt_prod)
            prod = res_prod.scalars().first()
            if prod:
                prod.stock = max(0, prod.stock - item.quantity)
            await delete_cache(f"product:{item.product_id}")
        await mysql_db.commit()
        await delete_cache("products:list")
            
    order.status = status
    await db.commit()
    await db.refresh(order)
    return order
async def get_product_sales(db: AsyncSession, product_id: int) -> dict:
    stmt = select(
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.subtotal).label('total_revenue')
    ).where(OrderItem.product_id == product_id)
    
    result = await db.execute(stmt)
    row = result.first()
    
    return {
        "product_id": product_id,
        "total_quantity_sold": row.total_quantity or 0,
        "total_revenue": row.total_revenue or 0.0
    }
