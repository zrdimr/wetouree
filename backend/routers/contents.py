from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database

router = APIRouter(prefix="/contents", tags=["contents"])

class ContentBase(BaseModel):
    type: str
    title: str
    body: str
    image_url: Optional[str] = None
    language: Optional[str] = "id"
    is_published: Optional[bool] = True

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    image_url: Optional[str] = None
    is_published: Optional[bool] = None

class Content(ContentBase):
    id: int

    class Config:
        from_attributes = True

@router.post("/", response_model=Content)
def create_content(content: ContentCreate, db: Session = Depends(database.get_db)):
    db_content = models.Content(**content.dict())
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

@router.get("/", response_model=List[Content])
def read_contents(db: Session = Depends(database.get_db), all: bool = True):
    query = db.query(models.Content)
    if not all:
        query = query.filter(models.Content.is_published == True)
    return query.all()

@router.get("/{content_id}", response_model=Content)
def read_content(content_id: int, db: Session = Depends(database.get_db)):
    content = db.query(models.Content).filter(models.Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.put("/{content_id}", response_model=Content)
def update_content(content_id: int, content_update: ContentUpdate, db: Session = Depends(database.get_db)):
    db_content = db.query(models.Content).filter(models.Content.id == content_id).first()
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    update_data = content_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_content, key, value)
    
    db.commit()
    db.refresh(db_content)
    return db_content

@router.delete("/{content_id}")
def delete_content(content_id: int, db: Session = Depends(database.get_db)):
    db_content = db.query(models.Content).filter(models.Content.id == content_id).first()
    if not db_content:
        raise HTTPException(status_code=404, detail="Content not found")
    db.delete(db_content)
    db.commit()
    return {"status": "success"}
