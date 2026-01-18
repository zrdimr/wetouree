from fastapi import FastAPI
from backend.database import engine, Base
from backend.routers import destinations, packages, bookings

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pulau Harapan Tourism API")

app.include_router(destinations.router)
app.include_router(packages.router)
app.include_router(bookings.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Pulau Harapan Tourism API"}
