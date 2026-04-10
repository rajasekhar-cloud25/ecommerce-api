from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, String
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship
from enum import Enum

class OrderStatus(str, Enum):
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    SHIPPED   = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED  = "refunded"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_items = relationship("OrderItem", back_populates="order")
    created_at = Column(DateTime, default=func.now())
    address_id = Column(Integer, ForeignKey('address.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    total_price = Column(Float)
    status = Column(String)
    stripe_payment_intent = Column(String, nullable=True)
    order_number = Column(String, unique=True, index=True, nullable=True)

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))  
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Float)
    quantity = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")