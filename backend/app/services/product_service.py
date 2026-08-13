import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from app.models.product import Product, Category, Supplier
from app.schemas.product import ProductCreate, ProductUpdate, CategoryCreate, ProductResponse
from app.services.cache_service import get_cache, set_cache, delete_cache
from app.services.event_service import log_event
from app.config import get_settings

settings = get_settings()

def _format_product(product: Product) -> dict:
    # Serialize product with category and supplier names for caching and response
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "category_id": product.category_id,
        "supplier_id": product.supplier_id,
        "sku": product.sku,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        "category_name": product.category.name if product.category else None,
        "supplier_name": product.supplier.name if product.supplier else None,
    }

async def get_products(db: AsyncSession) -> dict:
    cache_key = "products:list"
    cached = await get_cache(cache_key)
    if cached:
        return json.loads(cached)
    
    stmt = select(Product).options(joinedload(Product.category), joinedload(Product.supplier))
    result = await db.execute(stmt)
    products = result.scalars().all()
    
    formatted_products = [_format_product(p) for p in products]
    response_data = {"items": formatted_products, "total": len(formatted_products)}
    
    await set_cache(cache_key, response_data, settings.CACHE_TTL)
    return response_data

async def get_product(db: AsyncSession, product_id: int) -> dict:
    cache_key = f"product:{product_id}"
    cached = await get_cache(cache_key)
    if cached:
        return json.loads(cached)
    
    stmt = select(Product).options(joinedload(Product.category), joinedload(Product.supplier)).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    formatted_product = _format_product(product)
    await set_cache(cache_key, formatted_product, settings.CACHE_TTL)
    return formatted_product

async def create_product(db: AsyncSession, data: ProductCreate) -> dict:
    new_product = Product(**data.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    
    # Needs a separate query to load relations for format output
    stmt = select(Product).options(joinedload(Product.category), joinedload(Product.supplier)).where(Product.id == new_product.id)
    result = await db.execute(stmt)
    new_product_with_rels = result.scalars().first()
    
    await log_event(new_product_with_rels.id, "product_created", {"sku": new_product_with_rels.sku})
    await delete_cache("products:list")
    
    return _format_product(new_product_with_rels)

async def update_product(db: AsyncSession, product_id: int, data: ProductUpdate) -> dict:
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    update_data = data.model_dump(exclude_unset=True)
    old_price = product.price
    old_stock = product.stock
    
    for key, value in update_data.items():
        setattr(product, key, value)
        
    await db.commit()
    
    # Reload with relations
    stmt_rel = select(Product).options(joinedload(Product.category), joinedload(Product.supplier)).where(Product.id == product_id)
    res_rel = await db.execute(stmt_rel)
    updated_product = res_rel.scalars().first()
    
    # Log events
    if "price" in update_data and update_data["price"] != old_price:
        await log_event(product_id, "price_changed", {"old_price": old_price, "new_price": update_data["price"]})
    if "stock" in update_data and update_data["stock"] != old_stock:
        await log_event(product_id, "stock_updated", {"old_stock": old_stock, "new_stock": update_data["stock"]})
        
    await log_event(product_id, "product_updated", {"fields": list(update_data.keys())})
    
    await delete_cache("products:list")
    await delete_cache(f"product:{product_id}")
    
    return _format_product(updated_product)

async def delete_product(db: AsyncSession, product_id: int) -> None:
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalars().first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    await db.delete(product)
    await db.commit()
    
    await log_event(product_id, "product_deleted", {"sku": product.sku})
    await delete_cache("products:list")
    await delete_cache(f"product:{product_id}")

async def get_categories(db: AsyncSession) -> list:
    stmt = select(Category)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    new_category = Category(**data.model_dump())
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category
