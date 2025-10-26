from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    title: str
    description: str
    starting_price: int
    duration_hours: int

class ItemCreate(ItemBase):
    seller_id: int 

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    seller_id: int
    end_time: datetime | None
    active: bool
    remaining_time_seconds: int

    class Config:
        orm_mode = True
        from_attributes = True  



