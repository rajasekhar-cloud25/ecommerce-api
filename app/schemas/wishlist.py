from pydantic import BaseModel
from datetime import datetime

class AddToWishlist(BaseModel):
    product_id: int

    class Config:
        from_attributes = True

class WishlistResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True