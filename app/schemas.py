from pydantic import BaseModel
from datetime import datetime



class ItemBase(BaseModel):
    """base schema for catalogue items"""
    title: str
    description: str
    starting_price: int
    duration_hours: int

class ItemCreate(ItemBase):
    """schema for creating a new item"""
    seller_id: int 

class ItemResponse(ItemBase):
    """schema for returning item details"""
    id: int
    created_at: datetime
    seller_id: int
    end_time: datetime | None
    active: bool
    remaining_time_seconds: int

    class Config:
        orm_mode = True
        from_attributes = True  



