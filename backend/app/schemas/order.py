from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    product_name: str
    unit_price: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)

class OrderCreate(BaseModel):
    notes: Optional[str] = None
    items: List[OrderItemCreate]

class OrderResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None
    total_amount: float
    status: str
    notes: Optional[str] = None
    can_process: bool = False
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)

class OrderListResponse(BaseModel):
    items: List[OrderResponse]
    total: int

class SalesSummaryResponse(BaseModel):
    product_id: int
    total_quantity_sold: int
    total_revenue: float
