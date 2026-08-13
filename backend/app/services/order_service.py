from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate

async def get_orders(db: AsyncSession) -> dict:
    stmt = select(Order).options(joinedload(Order.items)).order_by(Order.created_at.desc())
    result = await db.execute(stmt)
    orders = result.unique().scalars().all()
    return {"items": orders, "total": len(orders)}

async def create_order(db: AsyncSession, data: OrderCreate) -> Order:
    new_order = Order(notes=data.notes, status="pending")
    db.add(new_order)
    await db.flush() # get new_order.id
    
    total_amount = 0.0
    for item_data in data.items:
        subtotal = item_data.quantity * item_data.unit_price
        total_amount += subtotal
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data.product_id,
            product_name=item_data.product_name,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            subtotal=subtotal
        )
        db.add(order_item)
        
    new_order.total_amount = total_amount
    await db.commit()
    
    # Refresh and load items
    stmt = select(Order).options(joinedload(Order.items)).where(Order.id == new_order.id)
    result = await db.execute(stmt)
    return result.unique().scalars().first()

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
