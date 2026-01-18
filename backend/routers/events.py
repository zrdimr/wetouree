from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from backend import models, database

router = APIRouter(prefix="/events", tags=["events"])

class EventBase(BaseModel):
    destination_id: int
    title: str
    description: str
    event_date: datetime
    image_url: Optional[str] = None

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    destination_name: Optional[str] = None

    class Config:
        from_attributes = True

@router.post("/", response_model=Event)
def create_event(event: EventCreate, db: Session = Depends(database.get_db)):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/", response_model=List[Event])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    events = db.query(models.Event).order_by(models.Event.event_date).offset(skip).limit(limit).all()
    result = []
    for event in events:
        event_dict = {
            "id": event.id,
            "destination_id": event.destination_id,
            "title": event.title,
            "description": event.description,
            "event_date": event.event_date,
            "image_url": event.image_url,
            "destination_name": event.destination.name if event.destination else None
        }
        result.append(event_dict)
    return result

@router.delete("/{event_id}")
def delete_event(event_id: int, db: Session = Depends(database.get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return {"message": "Event deleted"}
