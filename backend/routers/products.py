from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database

router = APIRouter(prefix="/products", tags=["products"])

class ProductBase(BaseModel):
    umkm_id: int
    name: str
    description: str
    price: float
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True

@router.post("/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(database.get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@router.get("/umkm/{umkm_id}", response_model=List[Product])
def read_products_by_umkm(umkm_id: int, db: Session = Depends(database.get_db)):
    products = db.query(models.Product).filter(models.Product.umkm_id == umkm_id).all()
    return products

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}
