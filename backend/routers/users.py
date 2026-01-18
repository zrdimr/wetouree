from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import hashlib

from backend.database import get_db
from backend.models import User

router = APIRouter(prefix="/users", tags=["users"])

# --- Pydantic Schemas ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    name: str
    phone: Optional[str] = None
    role: str = "visitor"
    assigned_area: Optional[str] = None
    profile_image: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    password: Optional[str] = None

class UserRoleUpdate(BaseModel):
    role: str
    assigned_area: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    name: str
    phone: Optional[str]
    role: str
    is_active: bool
    assigned_area: Optional[str]
    profile_image: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

# Role definitions
ROLES = {
    "visitor": {"label": "Pengunjung", "level": 1},
    "umkm_owner": {"label": "Pengelola UMKM", "level": 2},
    "umkm_admin": {"label": "Admin UMKM", "level": 3},
    "ticket_officer": {"label": "Petugas Tiket", "level": 3},
    "content_manager": {"label": "Content Manager", "level": 4},
    "area_manager": {"label": "Pengelola Kawasan", "level": 5},
    "tourism_officer": {"label": "Dinas Pariwisata", "level": 6},
    "regional_admin": {"label": "Administrator Wilayah", "level": 7},
    "superadmin": {"label": "Superadmin", "level": 10}
}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

# --- Endpoints ---

@router.get("/roles")
def get_roles():
    """Get all available roles"""
    return ROLES

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username sudah digunakan")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email sudah digunakan")
    
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        name=user.name,
        phone=user.phone,
        role=user.role if user.role in ROLES else "visitor",
        assigned_area=user.assigned_area,
        profile_image=user.profile_image
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username atau password salah")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Akun tidak aktif")
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "status": "success",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "role_label": ROLES.get(user.role, {}).get("label", user.role),
            "assigned_area": user.assigned_area,
            "profile_image": user.profile_image
        }
    }

@router.get("/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, role: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    if user_data.name:
        user.name = user_data.name
    if user_data.email:
        user.email = user_data.email
    if user_data.phone:
        user.phone = user_data.phone
    if user_data.profile_image:
        user.profile_image = user_data.profile_image
    if user_data.password:
        user.password_hash = hash_password(user_data.password)
    
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(user_id: int, role_data: UserRoleUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    if role_data.role not in ROLES:
        raise HTTPException(status_code=400, detail="Role tidak valid")
    
    user.role = role_data.role
    user.assigned_area = role_data.assigned_area
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/toggle-active")
def toggle_user_active(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    user.is_active = not user.is_active
    db.commit()
    return {"status": "success", "is_active": user.is_active}

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    
    db.delete(user)
    db.commit()
    return {"status": "deleted"}

# --- Stats Endpoint ---
@router.get("/stats/overview")
def get_user_stats(db: Session = Depends(get_db)):
    total = db.query(User).count()
    active = db.query(User).filter(User.is_active.is_(True)).count()
    by_role = {}
    for role in ROLES:
        count = db.query(User).filter(User.role == role).count()
        if count > 0:
            by_role[role] = count
    
    return {
        "total": total,
        "active": active,
        "inactive": total - active,
        "by_role": by_role
    }
