from pydantic import BaseModel
from app.schemas.cart import Cart

class CheckoutSession(BaseModel):
    user_id: int
    cart: Cart
    status: str = "pending" # pending, processing, completed
