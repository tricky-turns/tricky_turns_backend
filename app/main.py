from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.model import metadata
from app.database import database
from sqlalchemy.ext.asyncio import create_async_engine
import os
from app.auth import router as auth_router
from app.admin_auth import router as admin_auth_router
from app.admin_routes import router as admin_router


app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider tightening for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database engine for async schema creation
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=False)

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    await database.connect()
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Optional root route
@app.get("/")
def read_root():
    return {"message": "Tricky Turns backend is live."}

# Include API routes
app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/auth")
app.include_router(admin_auth_router, prefix="/admin")
app.include_router(admin_router, prefix="/admin")

