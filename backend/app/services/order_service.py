from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from fastapi import HTTPException
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate
from app.services.product_service import get_product

async def get_orders(db: AsyncSession, user_id: int = None) -> dict:
    stmt = select(Order).options(joinedload(Order.items)).order_by(Order.created_at.desc())
    if user_id is not None:
        stmt = stmt.where(Order.user_id == user_id)
        
    result = await db.execute(stmt)
    orders = result.unique().scalars().all()
    return {"items": orders, "total": len(orders)}

async def create_order(db: AsyncSession, pg_db: AsyncSession, data: OrderCreate, user_id: int) -> Order:
    new_order = Order(notes=data.notes, status="pending", user_id=user_id)
    db.add(new_order)
    await db.flush() # get new_order.id
    
    total_amount = 0.0
    for item_data in data.items:
        # BUG FIX: Fetch real product from PostgreSQL to get authentic price and name
        real_product = await get_product(pg_db, item_data.product_id)
        if not real_product:
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
            
        authentic_price = real_product.price
        authentic_name = real_product.name
        
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

async def update_order_status(db: AsyncSession, order_id: int, status: str) -> Order:
    stmt = select(Order).options(joinedload(Order.items)).where(Order.id == order_id)
    result = await db.execute(stmt)
    order = result.unique().scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
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
