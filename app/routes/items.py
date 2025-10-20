from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from .. import models, schemas
from ..database import SessionLocal

router = APIRouter(prefix="/catalogue", tags=["Catalogue"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_user(x_user: Optional[str] = Header(None)):
    if not x_user:
        raise HTTPException(status_code=401, detail="user not logged in")
    return x_user


@router.get("/items", response_model=list[schemas.ItemResponse])
def get_all_items(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    items = db.query(models.Item).filter(models.Item.active == True).all()

    response = []
    for item in items:
        remaining = max(int((item.end_time - now).total_seconds()), 0)
        if remaining == 0:
            item.active = False
            db.add(item)
            db.commit()
        else:
            data = item.__dict__.copy()
            data["remaining_time_seconds"] = remaining
            response.append(data)
    return response

@router.get("/search", response_model=list[schemas.ItemResponse])
def search_items(keyword: str, db: Session = Depends(get_db), x_user: str = Depends(require_user)):
    now = datetime.utcnow()
    results = db.query(models.Item).filter(
        models.Item.active == True,
        models.Item.title.ilike(f"%{keyword}%")
    ).all()
    response = []
    for item in results:
        remaining = max(int((item.end_time - now).total_seconds()), 0)
        item_dict = item.__dict__.copy()
        item_dict["remaining_time_seconds"] = remaining
        response.append(item_dict)
    return response

@router.post("/items", response_model=schemas.ItemResponse)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db), x_user: str = Depends(require_user)):
    seller = db.query(models.Seller).filter(models.Seller.id == item.seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="seller not found")

    now = datetime.utcnow()
    end_time = now + timedelta(hours=item.duration_hours)

    new_item = models.Item(
        title=item.title,
        description=item.description,
        starting_price=item.starting_price,
        current_price=item.starting_price, 
        duration_hours=item.duration_hours,
        created_at=now,
        end_time=end_time,
        seller_id=item.seller_id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)


    remaining = max(int((end_time - now).total_seconds()), 0)
    data = new_item.__dict__.copy()
    data["remaining_time_seconds"] = remaining
    return data

@router.post("/sellers")
def create_seller(name: str, email: str, db: Session = Depends(get_db)):
    seller = models.Seller(name=name, email=email)
    db.add(seller)
    db.commit()
    db.refresh(seller)
    return seller

@router.get("/sellers")
def get_all_sellers(db: Session = Depends(get_db)):
    return db.query(models.Seller).all()
