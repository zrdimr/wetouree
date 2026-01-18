from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database

router = APIRouter(prefix="/destinations", tags=["destinations"])

class DestinationBase(BaseModel):
    name: str
    description: str
    image_url: Optional[str] = None
    type: Optional[str] = "alam"
    status: Optional[str] = "open"
    capacity: Optional[int] = 100
    current_visitors: Optional[int] = 0
    weather_info: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DestinationCreate(DestinationBase):
    pass

class DestinationUpdate(BaseModel):
    status: Optional[str] = None
    current_visitors: Optional[int] = None
    weather_info: Optional[str] = None

class Destination(DestinationBase):
    id: int

    class Config:
        from_attributes = True

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

@router.get("/{destination_id}", response_model=Destination)
def read_destination(destination_id: int, db: Session = Depends(database.get_db)):
    destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    return destination

@router.put("/{destination_id}", response_model=Destination)
def update_destination(destination_id: int, update: DestinationUpdate, db: Session = Depends(database.get_db)):
    destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    if update.status is not None:
        destination.status = update.status
    if update.current_visitors is not None:
        destination.current_visitors = update.current_visitors
    if update.weather_info is not None:
        destination.weather_info = update.weather_info
    
    db.commit()
    db.refresh(destination)
    return destination

@router.delete("/{destination_id}")
def delete_destination(destination_id: int, db: Session = Depends(database.get_db)):
    destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")
    db.delete(destination)
    db.commit()
    return {"message": "Destination deleted"}
