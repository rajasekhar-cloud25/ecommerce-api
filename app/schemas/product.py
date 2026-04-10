from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CreateProduct(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    discount_percentage: Optional[float] = 0.0
    stock: int
    brand: Optional[str] = None
    images: Optional[str] = None
    is_published: Optional[bool] = False
    category_id: int

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    price: float
    discount_percentage: float
    stock: int
    brand: Optional[str] = None
    images: Optional[str] = None
    is_published: bool
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    discount_percentage: Optional[float] = 0.0
    stock: Optional[int] = None
    brand: Optional[str] = None
    images: Optional[str] = None
    is_published: Optional[bool] = False
    category_id: Optional[int] = None

    class Config:
        from_attributes = True