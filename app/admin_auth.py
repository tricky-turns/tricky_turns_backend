# app/admin_auth.py

from fastapi import APIRouter, HTTPException, status, Response, Cookie, Depends, Request
from app.model import admins, admin_audit_log
from app.database import database
from app.utils.password import hash_password, verify_password
from datetime import datetime
import secrets

router = APIRouter()
ADMIN_SESSION_COOKIE = "admin_session"
admin_sessions = {}

def log_admin_action(admin_username, action, target_table, target_id=None, notes=None):
    return admin_audit_log.insert().values(
        admin_username=admin_username,
        action=action,
        target_table=target_table,
        target_id=target_id,
        notes=notes,
        timestamp=datetime.utcnow()
    )

def get_current_admin(session_id: str = Cookie(None)):
    if session_id and session_id in admin_sessions:
        return admin_sessions[session_id]
    raise HTTPException(status_code=401, detail="Not authenticated as admin")

@router.post("/admin/login")
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
    # Create session
    session_id = secrets.token_urlsafe(32)
    admin_sessions[session_id] = {"id": admin["id"], "username": admin["username"]}
    response.set_cookie(ADMIN_SESSION_COOKIE, session_id, httponly=True, max_age=86400)
    await database.execute(log_admin_action(admin["username"], "login", "admins"))
    return {"message": "Logged in", "admin": admin["username"]}

@router.post("/admin/logout")
async def admin_logout(response: Response, session_id: str = Cookie(None), admin=Depends(get_current_admin)):
    if session_id and session_id in admin_sessions:
        del admin_sessions[session_id]
    response.delete_cookie(ADMIN_SESSION_COOKIE)
    await database.execute(log_admin_action(admin["username"], "logout", "admins"))
    return {"message": "Logged out"}

@router.get("/admin/me")
async def admin_me(admin=Depends(get_current_admin)):
    return {"admin": admin["username"]}
