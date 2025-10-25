from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship  
from datetime import datetime, timedelta
from .database import Base



class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    starting_price = Column(Integer)
    current_price = Column(Integer, default=0)  
    duration_hours = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    active = Column(Boolean, default=True)

    seller_id = Column(Integer)

    shipping_cost = Column(Integer, nullable=False, default=7)
    shipping_time = Column(Integer, nullable=False, default=3)
