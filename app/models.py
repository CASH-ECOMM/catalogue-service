from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship  
from datetime import datetime, timedelta
from .database import Base

class Seller(Base):
    __tablename__ = "sellers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    items = relationship("Item", back_populates="seller")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    starting_price = Column(Float)
    current_price = Column(Float, default=0.0)
    auction_type = Column(String, default="Forward")
    duration_hours = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    active = Column(Boolean, default=True)

    seller_id = Column(Integer, ForeignKey("sellers.id"))
    seller = relationship("Seller", back_populates="items")
