from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routers import destinations, packages, bookings, umkm, facilities, contents, tickets, products, feedback, events, rentals, guides, users

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pulau Harapan Tourism API",
    description="API untuk platform manajemen pariwisata Pulau Harapan",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users.router)
app.include_router(destinations.router)
app.include_router(packages.router)
app.include_router(bookings.router)
app.include_router(umkm.router)
app.include_router(facilities.router)
app.include_router(contents.router)
app.include_router(tickets.router)
app.include_router(products.router)
app.include_router(feedback.router)
app.include_router(events.router)
app.include_router(rentals.router)
app.include_router(guides.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Pulau Harapan Tourism API v2.0",
        "docs": "/docs",
        "endpoints": [
            "/destinations",
            "/packages",
            "/bookings",
            "/umkm",
            "/facilities",
            "/contents"
        ]
    }
