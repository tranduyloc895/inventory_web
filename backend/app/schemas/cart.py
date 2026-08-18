from pydantic import BaseModel, Field
from typing import List

class CartItem(BaseModel):
    product_id: int
    product_name: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)

class Cart(BaseModel):
    user_id: int
    items: List[CartItem] = []
    total_amount: float = 0.0

class AddToCartRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
