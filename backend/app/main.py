from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from sqlalchemy import text
from app.database.connection import SessionLocal
from app.database.connection import Base, engine
from app.models import MaintenanceTask, Asset, Schedule

from app.routers import tasks, assets, schedules


app = FastAPI(
    title="Railway AI Backend"
)

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)

Base.metadata.create_all(
    bind=engine
)


app.include_router(
    tasks.router
)

app.include_router(
    assets.router
)

app.include_router(
    schedules.router
)


@app.get("/")
def home():

    return {
        "status": "Backend Running"
    }

@app.get("/health")
def health():

    try:

        db = SessionLocal()

        db.execute(
            text("SELECT 1")
        )

        db.close()


        return {
            "status": "healthy",
            "database": "connected"
        }


    except Exception as e:

        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }