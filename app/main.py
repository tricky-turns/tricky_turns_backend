from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from app.routes import router
from app.model import metadata, leaderboard  # leaderboard import isn't required just for table creation
from app.database import database  # <- Needed to connect/disconnect
import os

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load DB URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Lifecycle events
@app.on_event("startup")
async def startup():
    await database.connect()
    metadata.create_all(engine)  # ← Automatically creates the schema

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Include your API routes
app.include_router(router)
