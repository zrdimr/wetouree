from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from backend import models, database

router = APIRouter(prefix="/destinations", tags=["destinations"])

class DestinationBase(BaseModel):
    name: str
    description: str
    image_url: str

class DestinationCreate(DestinationBase):
    pass

class Destination(DestinationBase):
    id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=Destination)
def create_destination(destination: DestinationCreate, db: Session = Depends(database.get_db)):
    db_destination = models.Destination(**destination.dict())
    db.add(db_destination)
    db.commit()
    db.refresh(db_destination)
    return db_destination

@router.get("/", response_model=List[Destination])
def read_destinations(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    destinations = db.query(models.Destination).offset(skip).limit(limit).all()
    return destinations

@router.delete("/{destination_id}")
def delete_destination(destination_id: int, db: Session = Depends(database.get_db)):
    destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    db.delete(destination)
    db.commit()
    return {"message": "Destination deleted"}
