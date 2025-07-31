# app/admin_auth.py

from fastapi import APIRouter, HTTPException, status, Response, Cookie, Depends, Request
from app.model import admins, admin_audit_log, admin_sessions  # Note: admin_sessions now imported from model.py
from app.database import database
from app.utils.password import hash_password, verify_password
from datetime import datetime, timedelta
import secrets

router = APIRouter()
ADMIN_SESSION_COOKIE = "admin_session"

def log_admin_action(admin_username, action, target_table, target_id=None, notes=None):
    return admin_audit_log.insert().values(
        admin_username=admin_username,
        action=action,
        target_table=target_table,
        target_id=target_id,
        notes=notes,
        timestamp=datetime.utcnow()
    )

async def get_current_admin(session_id: str = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated as admin")
    # Lookup session in DB, check expiry
    query = admin_sessions.select().where(admin_sessions.c.id == session_id)
    session = await database.fetch_one(query)
    if not session or (session["expires_at"] and session["expires_at"] < datetime.utcnow()):
        raise HTTPException(status_code=401, detail="Session expired or invalid")
    admin = await database.fetch_one(admins.select().where(admins.c.id == session["admin_id"]))
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")
    return {"id": admin["id"], "username": admin["username"]}

@router.post("/login")
async def admin_login(data: dict, response: Response):
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    query = admins.select().where(admins.c.username == username)
    admin = await database.fetch_one(query)
    if not admin or not verify_password(password, admin["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not admin["is_active"]:
        raise HTTPException(status_code=403, detail="Inactive admin account")
    session_id = secrets.token_urlsafe(32)
    now = datetime.utcnow()
    expires_at = now + timedelta(days=1)
    await database.execute(
        admin_sessions.insert().values(
            id=session_id,
            admin_id=admin["id"],
            created_at=now,
            expires_at=expires_at
        )
    )
    response.set_cookie(
        ADMIN_SESSION_COOKIE, session_id,
        httponly=True, max_age=86400, secure=True, samesite="strict"
    )
    await database.execute(log_admin_action(admin["username"], "login", "admins"))
    return {"message": "Logged in", "admin": admin["username"]}

@router.post("/logout")
async def admin_logout(response: Response, session_id: str = Cookie(None), admin=Depends(get_current_admin)):
    if session_id:
        await database.execute(admin_sessions.delete().where(admin_sessions.c.id == session_id))
    response.delete_cookie(ADMIN_SESSION_COOKIE)
    await database.execute(log_admin_action(admin["username"], "logout", "admins"))
    return {"message": "Logged out"}

@router.get("/me")
async def admin_me(admin=Depends(get_current_admin)):
    return {"admin": admin["username"]}
