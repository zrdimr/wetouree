from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database

router = APIRouter(prefix="/umkm", tags=["umkm"])

class UMKMBase(BaseModel):
    name: str
    description: str
    category: str
    image_url: Optional[str] = None
    location: Optional[str] = None
    rating: Optional[float] = 0.0
    is_verified: Optional[bool] = False

class UMKMCreate(UMKMBase):
    owner_id: Optional[int] = None

class UMKM(UMKMBase):
    id: int
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True

@router.post("/", response_model=UMKM)
def create_umkm(umkm: UMKMCreate, db: Session = Depends(database.get_db)):
    db_umkm = models.UMKM(**umkm.dict())
    db.add(db_umkm)
    db.commit()
    db.refresh(db_umkm)
    return db_umkm

@router.get("/", response_model=List[UMKM])
def read_umkm_list(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    umkm_list = db.query(models.UMKM).offset(skip).limit(limit).all()
    return umkm_list

@router.get("/{umkm_id}", response_model=UMKM)
def read_umkm(umkm_id: int, db: Session = Depends(database.get_db)):
    umkm = db.query(models.UMKM).filter(models.UMKM.id == umkm_id).first()
    if not umkm:
        raise HTTPException(status_code=404, detail="UMKM not found")
    return umkm

@router.delete("/{umkm_id}")
def delete_umkm(umkm_id: int, db: Session = Depends(database.get_db)):
    umkm = db.query(models.UMKM).filter(models.UMKM.id == umkm_id).first()
    if not umkm:
        raise HTTPException(status_code=404, detail="UMKM not found")
    db.delete(umkm)
    db.commit()
    return {"message": "UMKM deleted"}
