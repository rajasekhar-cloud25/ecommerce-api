from sqlalchemy import Column, Integer, Boolean, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    discount_percentage = Column(Float, nullable=False, default=0.0)
    is_available = Column(Boolean, nullable=False, default=True)
    is_published = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    stock = Column(Integer, nullable=False)
    brand = Column(String, nullable=True)
    images = Column(Text, nullable=False)
    category = relationship("Category")
    category_id = Column(Integer, ForeignKey('categories.id'))
