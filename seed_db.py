import os
import sys
import hashlib
from datetime import datetime, timedelta
from backend.database import SessionLocal, engine, Base
from backend import models

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create all tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# --- Seed Users ---
def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

users = [
    models.User(
        username="visitor", email="visitor@example.com",
        password_hash=hash_password("visitor123"), role="visitor",
        name="Budi Santoso", phone="081234567890"
    ),
    models.User(
        username="umkm_owner", email="umkm@example.com",
        password_hash=hash_password("umkm123"), role="umkm_owner",
        name="Ibu Maryam", phone="081234567891"
    ),
    models.User(
        username="umkm_admin", email="admin_umkm@example.com",
        password_hash=hash_password("admin123"), role="umkm_admin",
        name="Pak Joko", phone="081234567892"
    ),
    models.User(
        username="area_manager", email="manager@example.com",
        password_hash=hash_password("manager123"), role="area_manager",
        name="Pak Rahman", phone="081234567893", assigned_area="Zona Pantai Selatan"
    ),
    models.User(
        username="tourism_officer", email="dinas@example.com",
        password_hash=hash_password("dinas123"), role="tourism_officer",
        name="Ibu Sri Wahyuni", phone="081234567894"
    ),
    models.User(
        username="regional_admin", email="regional@example.com",
        password_hash=hash_password("regional123"), role="regional_admin",
        name="Pak Camat", phone="081234567895", assigned_area="Kepulauan Seribu Utara"
    ),
    models.User(
        username="superadmin", email="superadmin@example.com",
        password_hash=hash_password("superadmin123"), role="superadmin",
        name="Administrator Utama", phone="081234567896"
    ),
    models.User(
        username="ticket_officer", email="ticket@example.com",
        password_hash=hash_password("ticket123"), role="ticket_officer",
        name="Petugas Gerbang", phone="081234567897"
    ),
    models.User(
        username="content_manager", email="content@example.com",
        password_hash=hash_password("content123"), role="content_manager",
        name="Editor Konten", phone="081234567898"
    ),
]
db.add_all(users)
db.commit()

# --- Seed Destinations ---
destinations = [
    models.Destination(
        name="Pulau Macan",
        description="Eco-resort dengan terumbu karang yang indah dan cottage di atas air.",
        image_url="https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=800",
        type="alam",
        status="open",
        capacity=150,
        current_visitors=45,
        weather_info="Cerah, 28°C",
        latitude=-5.6123,
        longitude=106.5234
    ),
    models.Destination(
        name="Pulau Pramuka",
        description="Pusat administrasi Kepulauan Seribu dengan penangkaran penyu.",
        image_url="https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800",
        type="budaya",
        status="open",
        capacity=200,
        current_visitors=78,
        weather_info="Berawan, 27°C",
        latitude=-5.7321,
        longitude=106.6123
    ),
    models.Destination(
        name="Pulau Harapan",
        description="Surga snorkeling dengan spot sunset terbaik di Kepulauan Seribu.",
        image_url="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800",
        type="alam",
        status="open",
        capacity=180,
        current_visitors=92,
        weather_info="Cerah, 29°C",
        latitude=-5.6789,
        longitude=106.5789
    ),
    models.Destination(
        name="Pulau Tidung",
        description="Terkenal dengan Jembatan Cinta dan aktivitas water sport.",
        image_url="https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=800",
        type="buatan",
        status="open",
        capacity=250,
        current_visitors=156,
        weather_info="Cerah, 30°C",
        latitude=-5.8012,
        longitude=106.5012
    ),
]
db.add_all(destinations)
db.commit()

# --- Seed Facilities ---
facilities = [
    models.Facility(destination_id=1, name="Toilet Utama", type="toilet"),
    models.Facility(destination_id=1, name="Dermaga Parking", type="parking"),
    models.Facility(destination_id=1, name="Mushola Al-Bahar", type="mushola"),
    models.Facility(destination_id=2, name="Toilet Dermaga", type="toilet"),
    models.Facility(destination_id=2, name="Area UMKM", type="umkm_zone"),
    models.Facility(destination_id=3, name="Toilet Pantai", type="toilet"),
    models.Facility(destination_id=3, name="Mushola Pantai", type="mushola"),
]
db.add_all(facilities)
db.commit()

# --- Seed Packages ---
packages = [
    models.Package(
        name="Island Hopping Adventure",
        price=750000,
        features="Snorkeling,Lunch,Boat Transfer,Guide",
        destination_id=1
    ),
    models.Package(
        name="Sunset Paradise Tour",
        price=500000,
        features="Sunset Cruise,Dinner,Photography",
        destination_id=3
    ),
    models.Package(
        name="Full Day Explorer",
        price=1200000,
        features="3 Islands,All Meals,Snorkeling,Kayak",
        destination_id=2
    ),
]
db.add_all(packages)
db.commit()

# --- Seed UMKM ---
umkm_list = [
    models.UMKM(
        name="Warung Seafood Bu Ani",
        description="Seafood segar langsung dari nelayan lokal dengan bumbu khas.",
        category="kuliner",
        image_url="https://images.unsplash.com/photo-1579631542720-3a87824fff86?w=400",
        location="Pulau Harapan, Dermaga Utama",
        rating=4.5,
        is_verified=True
    ),
    models.UMKM(
        name="Kerajinan Kerang Ibu Siti",
        description="Souvenir unik dari kerang dan hasil laut.",
        category="souvenir",
        image_url="https://images.unsplash.com/photo-1590736969955-71cc94901144?w=400",
        location="Pulau Pramuka",
        rating=4.2,
        is_verified=True
    ),
    models.UMKM(
        name="Pak Budi Dive Guide",
        description="Guide berpengalaman 15 tahun untuk snorkeling dan diving.",
        category="guide",
        image_url="https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=400",
        location="Pulau Macan",
        rating=4.8,
        is_verified=True
    ),
    models.UMKM(
        name="Homestay Keluarga Harapan",
        description="Penginapan nyaman dengan suasana kekeluargaan.",
        category="homestay",
        image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400",
        location="Pulau Harapan",
        rating=4.3,
        is_verified=True
    ),
]
db.add_all(umkm_list)
db.commit()

# --- Seed Content ---
contents = [
    models.Content(
        type="news",
        title="Festival Bahari Kepulauan Seribu 2026",
        body="Menyambut tahun baru, Kepulauan Seribu mengadakan Festival Bahari dengan berbagai kegiatan menarik termasuk lomba perahu, festival kuliner, dan konser musik.",
        image_url="https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=800",
        is_published=True
    ),
    models.Content(
        type="promo",
        title="Diskon 20% untuk Paket Family",
        body="Nikmati diskon spesial 20% untuk pembelian paket wisata keluarga (min. 4 orang) selama bulan Januari-Februari 2026.",
        image_url="https://images.unsplash.com/photo-1559128010-7c1ad6e1b6a5?w=800",
        is_published=True
    ),
]
db.add_all(contents)
db.commit()

# --- Seed Events ---
events = [
    models.Event(
        destination_id=3,
        title="Sunset Yoga Session",
        description="Yoga santai di tepi pantai menyambut senja.",
        event_date=datetime.now() + timedelta(days=7),
        image_url="https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=400"
    ),
    models.Event(
        destination_id=1,
        title="Beach Cleanup Day",
        description="Aksi bersih-bersih pantai bersama komunitas pecinta lingkungan.",
        event_date=datetime.now() + timedelta(days=14),
        image_url="https://images.unsplash.com/photo-1567095761054-7a02e69e5c43?w=400"
    ),
]
db.add_all(events)
db.commit()

# --- Camping Equipment ---
equipment = [
    models.CampingEquipment(
        name="Tenda Dome 4 Orang",
        description="Tenda kapasitas 4 orang, waterproof, mudah dipasang.",
        category="tent",
        price_per_day=75000,
        stock=10,
        available=10,
        image_url="https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=400"
    ),
    models.CampingEquipment(
        name="Tenda Dome 2 Orang",
        description="Tenda compact untuk 2 orang, ringan dan praktis.",
        category="tent",
        price_per_day=50000,
        stock=15,
        available=15,
        image_url="https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?w=400"
    ),
    models.CampingEquipment(
        name="Sleeping Bag Premium",
        description="Sleeping bag tebal, nyaman untuk cuaca dingin pantai.",
        category="sleeping",
        price_per_day=25000,
        stock=25,
        available=25,
        image_url="https://images.unsplash.com/photo-1445308394109-4ec2920981b1?w=400"
    ),
    models.CampingEquipment(
        name="Matras Camping",
        description="Matras empuk untuk tidur lebih nyaman.",
        category="sleeping",
        price_per_day=15000,
        stock=30,
        available=30,
        image_url="https://images.unsplash.com/photo-1563299796-17596ed6b017?w=400"
    ),
    models.CampingEquipment(
        name="Kompor Portable",
        description="Kompor gas portable dengan tabung, aman dan efisien.",
        category="cooking",
        price_per_day=35000,
        stock=12,
        available=12,
        image_url="https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=400"
    ),
    models.CampingEquipment(
        name="Set Peralatan Masak",
        description="Panci, wajan, dan spatula camping set lengkap.",
        category="cooking",
        price_per_day=20000,
        stock=15,
        available=15,
        image_url="https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400"
    ),
    models.CampingEquipment(
        name="Lampu LED Camping",
        description="Lampu LED rechargeable, terang dan tahan lama.",
        category="lighting",
        price_per_day=15000,
        stock=20,
        available=20,
        image_url="https://images.unsplash.com/photo-1525177089949-b1488a0ea5b6?w=400"
    ),
    models.CampingEquipment(
        name="Senter Waterproof",
        description="Senter anti air, cocok untuk aktivitas pantai malam.",
        category="lighting",
        price_per_day=10000,
        stock=25,
        available=25,
        image_url="https://images.unsplash.com/photo-1507477338202-487281e6c27e?w=400"
    ),
]
db.add_all(equipment)
db.commit()

# --- Tour Guides ---
guides = [
    models.TourGuide(
        name="Ahmad Sulthon",
        description="Guide snorkeling berpengalaman 10 tahun. Mengenal semua spot snorkeling terbaik di Kepulauan Seribu. Ramah dan sabar mengajar pemula.",
        specialty="snorkeling",
        languages="Indonesian, English",
        price_per_day=350000,
        rating=4.9,
        phone="081234567001",
        image_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
    ),
    models.TourGuide(
        name="Rizky Pratama",
        description="Dive master bersertifikat PADI dengan pengalaman 8 tahun. Ahli dalam underwater photography.",
        specialty="diving",
        languages="Indonesian, English, Japanese",
        price_per_day=500000,
        rating=4.8,
        phone="081234567002",
        image_url="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400"
    ),
    models.TourGuide(
        name="Siti Rahmawati",
        description="Fotografer profesional yang bisa mendokumentasikan seluruh perjalanan Anda. Hasil foto langsung dikirim via WhatsApp.",
        specialty="photography",
        languages="Indonesian, English",
        price_per_day=400000,
        rating=4.7,
        phone="081234567003",
        image_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400"
    ),
    models.TourGuide(
        name="Budi Santoso",
        description="Guide lokal kelahiran Pulau Harapan. Mengenal sejarah, budaya, dan lokasi tersembunyi di kepulauan.",
        specialty="general",
        languages="Indonesian",
        price_per_day=250000,
        rating=4.6,
        phone="081234567004",
        image_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400"
    ),
    models.TourGuide(
        name="Dewi Lestari",
        description="Guide trekking dan hiking. Ahli dalam rute pantai dan mangrove. Membawa P3K dan alat keselamatan.",
        specialty="trekking",
        languages="Indonesian, English",
        price_per_day=300000,
        rating=4.5,
        phone="081234567005",
        image_url="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400"
    ),
]
db.add_all(guides)
db.commit()

db.close()
print("✅ Database seeded successfully with expanded data!")
