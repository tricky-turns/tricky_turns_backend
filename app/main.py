from fastapi import FastAPI
from app.routes import router
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from app.model import metadata, leaderboard

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can change this to ["http://0.0.0.0:8000"] for stricter control
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    metadata.create_all(engine)  # ← create tables if not exist

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(router)
