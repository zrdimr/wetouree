from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database

router = APIRouter(prefix="/packages", tags=["packages"])

class PackageBase(BaseModel):
    name: str
    price: float
    features: str

class PackageCreate(PackageBase):
    pass

class Package(PackageBase):
    id: int

    class Config:
        orm_mode = True

@router.post("/", response_model=Package)
def create_package(package: PackageCreate, db: Session = Depends(database.get_db)):
    db_package = models.Package(**package.dict())
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package

@router.get("/", response_model=List[Package])
def read_packages(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    packages = db.query(models.Package).offset(skip).limit(limit).all()
    return packages

@router.get("/{package_id}", response_model=Package)
def read_package(package_id: int, db: Session = Depends(database.get_db)):
    package = db.query(models.Package).filter(models.Package.id == package_id).first()
    if package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return package

@router.delete("/{package_id}")
def delete_package(package_id: int, db: Session = Depends(database.get_db)):
    package = db.query(models.Package).filter(models.Package.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    db.delete(package)
    db.commit()
    return {"message": "Package deleted"}
