from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database

router = APIRouter(prefix="/guides", tags=["guides"])

# --- Guide Schemas ---
class GuideBase(BaseModel):
    name: str
    description: str
    specialty: str
    languages: str
    price_per_day: float
    phone: Optional[str] = None
    image_url: Optional[str] = None

class GuideCreate(GuideBase):
    pass

class Guide(GuideBase):
    id: int
    rating: float
    is_available: bool

    class Config:
        from_attributes = True

# --- Booking Schemas ---
class GuideBookingBase(BaseModel):
    guide_id: int
    customer_name: str
    customer_phone: str
    booking_date: str
    duration_days: int = 1
    notes: Optional[str] = None

class GuideBookingCreate(GuideBookingBase):
    pass

class GuideBooking(GuideBookingBase):
    id: int
    total_price: float
    status: str
    guide_name: Optional[str] = None

    class Config:
        from_attributes = True

# --- Guide Endpoints ---
@router.get("/", response_model=List[Guide])
def get_all_guides(db: Session = Depends(database.get_db)):
    guides = db.query(models.TourGuide).all()
    return guides

@router.get("/available", response_model=List[Guide])
def get_available_guides(db: Session = Depends(database.get_db)):
    guides = db.query(models.TourGuide).filter(models.TourGuide.is_available.is_(True)).all()
    return guides

@router.get("/{guide_id}", response_model=Guide)
def get_guide(guide_id: int, db: Session = Depends(database.get_db)):
    guide = db.query(models.TourGuide).filter(models.TourGuide.id == guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    return guide

@router.post("/", response_model=Guide)
def create_guide(guide: GuideCreate, db: Session = Depends(database.get_db)):
    db_guide = models.TourGuide(**guide.dict())
    db.add(db_guide)
    db.commit()
    db.refresh(db_guide)
    return db_guide

# --- Booking Endpoints ---
@router.get("/bookings/", response_model=List[GuideBooking])
def get_all_bookings(db: Session = Depends(database.get_db)):
    bookings = db.query(models.GuideBooking).all()
    result = []
    for booking in bookings:
        result.append({
            "id": booking.id,
            "guide_id": booking.guide_id,
            "customer_name": booking.customer_name,
            "customer_phone": booking.customer_phone,
            "booking_date": booking.booking_date,
            "duration_days": booking.duration_days,
            "notes": booking.notes,
            "total_price": booking.total_price,
            "status": booking.status,
            "guide_name": booking.guide.name if booking.guide else None
        })
    return result

@router.post("/bookings/", response_model=GuideBooking)
def create_booking(booking: GuideBookingCreate, db: Session = Depends(database.get_db)):
    guide = db.query(models.TourGuide).filter(models.TourGuide.id == booking.guide_id).first()
    if not guide:
        raise HTTPException(status_code=404, detail="Guide not found")
    
    total_price = guide.price_per_day * booking.duration_days
    
    db_booking = models.GuideBooking(
        **booking.dict(),
        total_price=total_price
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return {
        **booking.dict(),
        "id": db_booking.id,
        "total_price": total_price,
        "status": db_booking.status,
        "guide_name": guide.name
    }

@router.put("/bookings/{booking_id}/status")
def update_booking_status(booking_id: int, status: str, db: Session = Depends(database.get_db)):
    booking = db.query(models.GuideBooking).filter(models.GuideBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = status
    db.commit()
    return {"message": "Booking status updated"}
