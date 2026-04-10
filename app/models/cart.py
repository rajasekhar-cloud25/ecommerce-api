from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User")

    cart_items = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    cart_id = Column(Integer, ForeignKey('carts.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)

    product = relationship("Product")
    cart = relationship("Cart", back_populates="cart_items")
