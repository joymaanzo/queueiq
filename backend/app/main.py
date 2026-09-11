"""
QueueIQ FastAPI application.

Phase A: /health and /clinics only.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app.models import Clinic


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="QueueIQ API",
    version="0.1.0",
    description="Bayesian clinic queue prediction platform (Module 2 MVP)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "QueueIQ API",
        "docs": "/docs",
        "health": "/health",
        "clinics": "/clinics",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "database": "connected",
        "model_loaded": False,
    }


@app.get("/clinics")
def list_clinics():
    db = SessionLocal()
    try:
        clinics = db.query(Clinic).all()
        return [
            {
                "clinic_id": c.clinic_id,
                "name": c.name,
                "location": c.location,
                "service_type": c.service_type,
                "hours_open": c.hours_open,
                "days_open": c.days_open,
            }
            for c in clinics
        ]
    finally:
        db.close()
