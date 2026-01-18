from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database

router = APIRouter(prefix="/facilities", tags=["facilities"])

class FacilityBase(BaseModel):
    destination_id: int
    name: str
    type: str
    coordinates: Optional[str] = None

class FacilityCreate(FacilityBase):
    pass

class Facility(FacilityBase):
    id: int

    class Config:
        from_attributes = True

@router.post("/", response_model=Facility)
def create_facility(facility: FacilityCreate, db: Session = Depends(database.get_db)):
    db_facility = models.Facility(**facility.dict())
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility

@router.get("/", response_model=List[Facility])
def read_facilities(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    facilities = db.query(models.Facility).offset(skip).limit(limit).all()
    return facilities
