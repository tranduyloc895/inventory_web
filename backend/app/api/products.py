from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database.postgres import get_pg_session
from app.database.mysql import get_mysql_session
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate, ProductListResponse, CategoryResponse, CategoryCreate
from app.schemas.order import SalesSummaryResponse
from app.services import product_service, order_service
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/categories/all", response_model=List[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_mysql_session)):
    return await product_service.get_categories(db)

@router.post("/categories", response_model=CategoryResponse)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_mysql_session)):
    return await product_service.create_category(db, data)

@router.get("/", response_model=ProductListResponse)
async def list_products(db: AsyncSession = Depends(get_mysql_session)):
    return await product_service.get_products(db)

@router.get("/{id}", response_model=ProductResponse)
async def get_product(id: int, db: AsyncSession = Depends(get_mysql_session)):
    return await product_service.get_product(db, id)

@router.post("/", response_model=ProductResponse)
async def create_product(
    data: ProductCreate, 
    db: AsyncSession = Depends(get_mysql_session),
    current_user: User = Depends(get_current_user)
):
    return await product_service.create_product(db, data, current_user.id)

@router.put("/{id}", response_model=ProductResponse)
async def update_product(
    id: int, 
    data: ProductUpdate, 
    db: AsyncSession = Depends(get_mysql_session),
    current_user: User = Depends(get_current_user)
):
    return await product_service.update_product(db, id, data, current_user)

@router.delete("/{id}", status_code=204)
async def delete_product(
    id: int, 
    db: AsyncSession = Depends(get_mysql_session),
    pg_db: AsyncSession = Depends(get_pg_session),
    current_user: User = Depends(get_current_user)
):
    await product_service.delete_product(db, pg_db, id, current_user)
    return None

@router.get("/{id}/sales", response_model=SalesSummaryResponse)
async def get_product_sales(id: int, db: AsyncSession = Depends(get_pg_session)):
    return await order_service.get_product_sales(db, id)
