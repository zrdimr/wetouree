from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database

router = APIRouter(prefix="/bookings", tags=["bookings"])

class BookingBase(BaseModel):
    customer_name: str
    email: str
    package_id: int
    date: str
    status: str = "pending"
    num_visitors: Optional[int] = 1
    total_price: Optional[float] = None

class BookingCreate(BookingBase):
    pass

class BookingStatusUpdate(BaseModel):
    status: str

class Booking(BookingBase):
    id: int

    class Config:
        from_attributes = True

@router.post("/", response_model=Booking)
def create_booking(booking: BookingCreate, db: Session = Depends(database.get_db)):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.get("/", response_model=List[Booking])
def read_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    bookings = db.query(models.Booking).offset(skip).limit(limit).all()
    return bookings

@router.get("/{booking_id}", response_model=Booking)
def read_booking(booking_id: int, db: Session = Depends(database.get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.put("/{booking_id}/status", response_model=Booking)
def update_booking_status(booking_id: int, status_update: BookingStatusUpdate, db: Session = Depends(database.get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = status_update.status
    db.commit()
    db.refresh(booking)
    return booking
