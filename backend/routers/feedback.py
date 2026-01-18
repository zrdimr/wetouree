from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database
from datetime import datetime

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackBase(BaseModel):
    type: str  # complaint, suggestion, emergency, review
    subject: str
    message: str
    destination_id: Optional[int] = None
    priority: Optional[str] = "normal"

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None

class Feedback(FeedbackBase):
    id: int
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

@router.post("/", response_model=Feedback)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(database.get_db)):
    db_feedback = models.Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/", response_model=List[Feedback])
def read_feedback_list(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    feedback_list = db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).offset(skip).limit(limit).all()
    return feedback_list

@router.get("/emergency", response_model=List[Feedback])
def read_emergency_list(db: Session = Depends(database.get_db)):
    """Get all emergency reports"""
    emergencies = db.query(models.Feedback).filter(models.Feedback.type == "emergency").all()
    return emergencies

@router.put("/{feedback_id}", response_model=Feedback)
def update_feedback(feedback_id: int, update: FeedbackUpdate, db: Session = Depends(database.get_db)):
    feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    if update.status:
        feedback.status = update.status
    if update.priority:
        feedback.priority = update.priority
    
    db.commit()
    db.refresh(feedback)
    return feedback
