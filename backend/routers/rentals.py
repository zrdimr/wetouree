from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from backend import models, database

router = APIRouter(prefix="/rentals", tags=["rentals"])

# --- Equipment Schemas ---
class EquipmentBase(BaseModel):
    name: str
    description: str
    category: str
    price_per_day: float
    stock: int = 1
    image_url: Optional[str] = None

class EquipmentCreate(EquipmentBase):
    pass

class Equipment(EquipmentBase):
    id: int
    available: int
    is_available: bool

    class Config:
        from_attributes = True

# --- Rental Schemas ---
class RentalBase(BaseModel):
    equipment_id: int
    customer_name: str
    customer_phone: str
    rental_date: str
    return_date: str
    quantity: int = 1

class RentalCreate(RentalBase):
    pass

class Rental(RentalBase):
    id: int
    total_price: float
    status: str
    equipment_name: Optional[str] = None

    class Config:
        from_attributes = True

# --- Equipment Endpoints ---
@router.get("/equipment", response_model=List[Equipment])
def get_all_equipment(db: Session = Depends(database.get_db)):
    equipment = db.query(models.CampingEquipment).all()
    return equipment

@router.get("/equipment/available", response_model=List[Equipment])
def get_available_equipment(db: Session = Depends(database.get_db)):
    equipment = db.query(models.CampingEquipment).filter(
        models.CampingEquipment.is_available == True,
        models.CampingEquipment.available > 0
    ).all()
    return equipment

@router.post("/equipment", response_model=Equipment)
def create_equipment(equipment: EquipmentCreate, db: Session = Depends(database.get_db)):
    db_equipment = models.CampingEquipment(**equipment.dict(), available=equipment.stock)
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

@router.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(database.get_db)):
    equipment = db.query(models.CampingEquipment).filter(models.CampingEquipment.id == equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    db.delete(equipment)
    db.commit()
    return {"message": "Equipment deleted"}

# --- Rental Endpoints ---
@router.get("/", response_model=List[Rental])
def get_all_rentals(db: Session = Depends(database.get_db)):
    rentals = db.query(models.EquipmentRental).all()
    result = []
    for rental in rentals:
        rental_dict = {
            "id": rental.id,
            "equipment_id": rental.equipment_id,
            "customer_name": rental.customer_name,
            "customer_phone": rental.customer_phone,
            "rental_date": rental.rental_date,
            "return_date": rental.return_date,
            "quantity": rental.quantity,
            "total_price": rental.total_price,
            "status": rental.status,
            "equipment_name": rental.equipment.name if rental.equipment else None
        }
        result.append(rental_dict)
    return result

@router.post("/", response_model=Rental)
def create_rental(rental: RentalCreate, db: Session = Depends(database.get_db)):
    # Get equipment and calculate price
    equipment = db.query(models.CampingEquipment).filter(models.CampingEquipment.id == rental.equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    if equipment.available < rental.quantity:
        raise HTTPException(status_code=400, detail="Not enough equipment available")
    
    # Calculate total price (simple: days * price * quantity)
    from datetime import datetime
    try:
        start = datetime.strptime(rental.rental_date, "%Y-%m-%d")
        end = datetime.strptime(rental.return_date, "%Y-%m-%d")
        days = max((end - start).days, 1)
    except:
        days = 1
    
    total_price = days * equipment.price_per_day * rental.quantity
    
    # Create rental
    db_rental = models.EquipmentRental(
        **rental.dict(),
        total_price=total_price
    )
    db.add(db_rental)
    
    # Update equipment availability
    equipment.available -= rental.quantity
    
    db.commit()
    db.refresh(db_rental)
    
    return {
        **rental.dict(),
        "id": db_rental.id,
        "total_price": total_price,
        "status": db_rental.status,
        "equipment_name": equipment.name
    }

@router.put("/{rental_id}/status")
def update_rental_status(rental_id: int, status: str, db: Session = Depends(database.get_db)):
    rental = db.query(models.EquipmentRental).filter(models.EquipmentRental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    
    old_status = rental.status
    rental.status = status
    
    # If returned, add back to available
    if status == "returned" and old_status != "returned":
        equipment = db.query(models.CampingEquipment).filter(models.CampingEquipment.id == rental.equipment_id).first()
        if equipment:
            equipment.available += rental.quantity
    
    db.commit()
    return {"message": "Rental status updated"}
