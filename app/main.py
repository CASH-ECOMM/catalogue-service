from fastapi import FastAPI
from . import models
from .database import engine
from .routes import items

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auction Catalogue Service")

app.include_router(items.router)

@app.get("/")
def root():
    return {"message": "Auction Catalogue Service"}
