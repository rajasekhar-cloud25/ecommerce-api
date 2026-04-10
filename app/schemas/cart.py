from pydantic import BaseModel

class AddToCart(BaseModel):
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    user_id: int
    cart_items: list[CartItemResponse] = []

    class Config:
        from_attributes = True

class UpdateQuantity(BaseModel):
    quantity: int