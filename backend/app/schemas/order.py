from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class OrderItemBase(BaseModel):
    product_id: int
    product_name: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    subtotal: float

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    notes: Optional[str] = None
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    total_amount: float
    status: str
    notes: Optional[str] = None
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)

class OrderListResponse(BaseModel):
    items: List[OrderResponse]
    total: int

class SalesSummaryResponse(BaseModel):
    product_id: int
    total_quantity_sold: int
    total_revenue: float
