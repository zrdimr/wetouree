from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime

# --- User & RBAC ---
# Roles: visitor, umkm_owner, umkm_admin, area_manager, tourism_officer, 
#        regional_admin, superadmin, ticket_officer, content_manager
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    name = Column(String)
    phone = Column(String, nullable=True)
    role = Column(String, default="visitor")
    is_active = Column(Boolean, default=True)
    profile_image = Column(String, nullable=True)
    assigned_area = Column(String, nullable=True)  # For area_manager, regional_admin
    firebase_uid = Column(String, nullable=True, unique=True)  # Firebase integration
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

# --- Destination Management ---
class Destination(Base):
    __tablename__ = "destinations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    image_url = Column(String)
    type = Column(String, default="alam")  # alam, budaya, buatan
    status = Column(String, default="open")  # open, closed, maintenance
    capacity = Column(Integer, default=100)
    current_visitors = Column(Integer, default=0)
    weather_info = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    facilities = relationship("Facility", back_populates="destination")
    events = relationship("Event", back_populates="destination")

class Facility(Base):
    __tablename__ = "facilities"
    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"))
    name = Column(String)
    type = Column(String)  # toilet, parking, mushola, umkm_zone
    coordinates = Column(String, nullable=True)  # JSON string for lat/lng
    
    destination = relationship("Destination", back_populates="facilities")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"))
    title = Column(String)
    description = Column(Text)
    event_date = Column(DateTime)
    image_url = Column(String, nullable=True)
    
    destination = relationship("Destination", back_populates="events")

# --- Visitor Management & Ticketing ---
class Package(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    features = Column(Text)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=True)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    qr_code = Column(String, unique=True)
    status = Column(String, default="valid")  # valid, used, expired
    check_in_time = Column(DateTime, nullable=True)
    
    booking = relationship("Booking", back_populates="ticket")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    email = Column(String)
    package_id = Column(Integer, ForeignKey("packages.id"))
    date = Column(String)
    status = Column(String, default="pending")  # pending, confirmed, cancelled, completed
    num_visitors = Column(Integer, default=1)
    total_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ticket = relationship("Ticket", back_populates="booking", uselist=False)

# --- UMKM & Local Experience ---
class UMKM(Base):
    __tablename__ = "umkm"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, index=True)
    description = Column(Text)
    category = Column(String)  # kuliner, souvenir, guide, homestay, workshop
    image_url = Column(String, nullable=True)
    location = Column(String, nullable=True)
    rating = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    umkm_id = Column(Integer, ForeignKey("umkm.id"))
    name = Column(String)
    description = Column(Text)
    price = Column(Float)
    image_url = Column(String, nullable=True)

# --- Smart Promotion & Content ---
class Content(Base):
    __tablename__ = "contents"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # news, event, promo, itinerary
    title = Column(String)
    body = Column(Text)
    image_url = Column(String, nullable=True)
    language = Column(String, default="id")  # id, en
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Feedback & Safety ---
class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # complaint, suggestion, emergency, review
    subject = Column(String)
    message = Column(Text)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=True)
    status = Column(String, default="open")  # open, in_progress, resolved
    priority = Column(String, default="normal")  # low, normal, high, critical
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Analytics (for storing aggregated data) ---
class VisitorStats(Base):
    __tablename__ = "visitor_stats"
    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"))
    date = Column(String)
    visitor_count = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)

# --- Camping Equipment Rental ---
class CampingEquipment(Base):
    __tablename__ = "camping_equipment"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    category = Column(String)  # tent, sleeping, cooking, lighting, other
    price_per_day = Column(Float)
    stock = Column(Integer, default=1)
    available = Column(Integer, default=1)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)

class EquipmentRental(Base):
    __tablename__ = "equipment_rentals"
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("camping_equipment.id"))
    customer_name = Column(String)
    customer_phone = Column(String)
    rental_date = Column(String)
    return_date = Column(String)
    quantity = Column(Integer, default=1)
    total_price = Column(Float)
    status = Column(String, default="pending")  # pending, active, returned, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    
    equipment = relationship("CampingEquipment")

# --- Tour Guide / Teman Main ---
class TourGuide(Base):
    __tablename__ = "tour_guides"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    specialty = Column(String)  # snorkeling, diving, trekking, photography, general
    languages = Column(String)  # JSON array: ["Indonesian", "English"]
    price_per_day = Column(Float)
    rating = Column(Float, default=0.0)
    phone = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)

class GuideBooking(Base):
    __tablename__ = "guide_bookings"
    id = Column(Integer, primary_key=True, index=True)
    guide_id = Column(Integer, ForeignKey("tour_guides.id"))
    customer_name = Column(String)
    customer_phone = Column(String)
    booking_date = Column(String)
    duration_days = Column(Integer, default=1)
    notes = Column(Text, nullable=True)
    total_price = Column(Float)
    status = Column(String, default="pending")  # pending, confirmed, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    
    guide = relationship("TourGuide")
