from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database
from datetime import datetime
import uuid

router = APIRouter(prefix="/tickets", tags=["tickets"])

class TicketBase(BaseModel):
    booking_id: int
    qr_code: Optional[str] = None
    status: Optional[str] = "valid"

class TicketCreate(BaseModel):
    booking_id: int

class Ticket(TicketBase):
    id: int
    check_in_time: Optional[str] = None

    class Config:
        from_attributes = True

class CheckInRequest(BaseModel):
    qr_code: str

@router.post("/", response_model=Ticket)
def create_ticket(ticket: TicketCreate, db: Session = Depends(database.get_db)):
    # Generate unique QR code
    qr_code = f"PH-{ticket.booking_id}-{uuid.uuid4().hex[:8].upper()}"
    
    db_ticket = models.Ticket(
        booking_id=ticket.booking_id,
        qr_code=qr_code,
        status="valid"
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.get("/", response_model=List[Ticket])
def read_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    tickets = db.query(models.Ticket).offset(skip).limit(limit).all()
    return tickets

@router.get("/booking/{booking_id}", response_model=Ticket)
def get_ticket_by_booking(booking_id: int, db: Session = Depends(database.get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.booking_id == booking_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found for this booking")
    return ticket

@router.post("/check-in")
def check_in_ticket(request: CheckInRequest, db: Session = Depends(database.get_db)):
    """Process check-in using QR code"""
    ticket = db.query(models.Ticket).filter(models.Ticket.qr_code == request.qr_code).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if ticket.status == "used":
        raise HTTPException(status_code=400, detail="Ticket already used")
    
    if ticket.status == "expired":
        raise HTTPException(status_code=400, detail="Ticket expired")
    
    # Mark ticket as used
    ticket.status = "used"
    ticket.check_in_time = datetime.utcnow()
    
    # Get booking to find destination and update visitor count
    booking = db.query(models.Booking).filter(models.Booking.id == ticket.booking_id).first()
    if booking:
        package = db.query(models.Package).filter(models.Package.id == booking.package_id).first()
        if package and package.destination_id:
            destination = db.query(models.Destination).filter(models.Destination.id == package.destination_id).first()
            if destination:
                destination.current_visitors += booking.num_visitors if booking.num_visitors else 1
    
    db.commit()
    
    return {
        "success": True,
        "message": "Check-in successful!",
        "ticket_id": ticket.id,
        "check_in_time": str(ticket.check_in_time)
    }

@router.get("/validate/{qr_code}")
def validate_ticket(qr_code: str, db: Session = Depends(database.get_db)):
    """Validate a ticket without checking in"""
    ticket = db.query(models.Ticket).filter(models.Ticket.qr_code == qr_code).first()
    
    if not ticket:
        return {"valid": False, "message": "Ticket not found"}
    
    booking = db.query(models.Booking).filter(models.Booking.id == ticket.booking_id).first()
    
    return {
        "valid": ticket.status == "valid",
        "status": ticket.status,
        "booking": {
            "customer_name": booking.customer_name if booking else None,
            "date": booking.date if booking else None,
            "num_visitors": booking.num_visitors if booking else 1
        }
    }
