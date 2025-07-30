# auth.py

from fastapi import APIRouter, HTTPException, Header
import httpx
import logging
from app.database import database
from app.model import users
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header")
        raise HTTPException(status_code=401, detail="Missing or invalid access token")
    token = authorization.split("Bearer ")[1]

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            pi_response = await client.get(
                "https://api.minepi.com/v2/me",
                headers={"Authorization": f"Bearer {token}"}
            )
        except httpx.RequestError as e:
            logger.error(f"Error connecting to Pi Platform API: {e}")
            raise HTTPException(status_code=500, detail="Failed to verify token")

    if pi_response.status_code == 401:
        logger.info("Pi token verification failed (invalid token)")
        raise HTTPException(status_code=401, detail="Invalid Pi access token")

    if pi_response.status_code != 200:
        logger.error(f"Unexpected status from Pi API: {pi_response.status_code}")
        raise HTTPException(status_code=500, detail="Error verifying Pi token")

    data = pi_response.json()
    username = data.get("username")
    if not username:
        logger.error("UserDTO missing username field from Pi")
        raise HTTPException(status_code=401, detail="Invalid Pi user data")
    
    # --- Begin new user auto-creation logic ---
    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)
    if not user:
        # Create user record
        await database.execute(
            users.insert().values(
                username=username,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow(),
                is_banned=False
            )
        )
        logger.info(f"Created new Pi user in DB: {username}")
    else:
        # Update last_login for returning users (optional)
        await database.execute(
            users.update().where(users.c.username == username).values(
                last_login=datetime.utcnow()
            )
        )
    # --- End new user auto-creation logic ---

    logger.info(f"Verified Pi user: {username}")
    return {"username": username}
