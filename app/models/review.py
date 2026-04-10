from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, String
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class CustomerReview(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Float, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    comment = Column(String, nullable=False)
    user = relationship("User")
