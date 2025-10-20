from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    title: str
    description: str
    starting_price: float
    duration_hours: int

class ItemCreate(ItemBase):
    seller_id: int 

class ItemResponse(ItemBase):
    id: int
    auction_type: str
    created_at: datetime
    seller_id: int
    current_price: float
    end_time: datetime
    active: bool
    remaining_time_seconds: int

    class Config:
        orm_mode = True
