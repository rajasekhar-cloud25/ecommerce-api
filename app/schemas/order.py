from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    user_id: int
    address_id: int
    items: list[OrderItemCreate]

    class Config:
        from_attributes = True

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    address_id: int
    status: str
    total_price: float
    created_at: datetime
    order_items: list[OrderItemResponse]

    class Config:
        from_attributes = True

class UpdateOrderStatus(BaseModel):
    status: str

    class Config:
        from_attributes = True