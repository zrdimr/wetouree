from backend.database import SessionLocal, engine, Base
from backend import models

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Destinations
if not db.query(models.Destination).first():
    # Island Hopping - Beautiful tropical island view
    dest1 = models.Destination(name="Island Hopping", description="Visit neighboring islands like Pulau Perak and Pulau Bulat.", image_url="https://images.unsplash.com/photo-1540206351-d6465b3ac5c1?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80")
    # Snorkeling - Clear blue water with fish
    dest2 = models.Destination(name="Snorkeling Spots", description="Explore the vibrant marine life and coral gardens.", image_url="https://images.unsplash.com/photo-1576402187880-abcda2aef5c0?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80")
    dest3 = models.Destination(name="Sunset Point", description="Witness breathtaking sunsets from the best vantage points in Kepulauan Seribu.", image_url="https://images.unsplash.com/photo-1473116763249-2faaef81ccda?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80")
    db.add_all([dest1, dest2, dest3])

# Packages
if not db.query(models.Package).first():
    pkg1 = models.Package(name="One Day Trip", price=350000, features="Speedboat Transfer,Lunch,Snorkeling Gear")
    pkg2 = models.Package(name="2D1N Stay", price=850000, features="Homestay AC,3x Meals,BBQ Night,Island Hopping")
    db.add_all([pkg1, pkg2])

db.commit()
db.close()
print("Database seeded!")
