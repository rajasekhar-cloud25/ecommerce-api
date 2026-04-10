from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ReviewCreate(BaseModel):
    rating: float
    comment: str
    product_id: int

    class Config:
        from_attributes = True

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    rating: float
    comment: str
    created_at: datetime
    product_id: int


    class Config:
        from_attributes = True

class ReviewUpdate(BaseModel):
    rating: Optional[float] = None
    comment: Optional[str] = None

    class Config:
        from_attributes = True