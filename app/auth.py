# auth.py

from fastapi import APIRouter, HTTPException, Header, Depends, status, Request
import requests
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# This is the reusable dependency to verify the Pi access token and return user info.
async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header")
        raise HTTPException(status_code=401, detail="Missing or invalid access token")
    token = authorization.split("Bearer ")[1]

    try:
        pi_response = requests.get(
            "https://api.minepi.com/v2/me",
            headers={"Authorization": f"Bearer {token}"}
        )
    except requests.RequestException as e:
        logger.error(f"Error connecting to Pi Platform API: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify token")

    if pi_response.status_code == 401:
        logger.info("Pi token verification failed (invalid token)")
        raise HTTPException(status_code=401, detail="Invalid Pi access token")

    data = pi_response.json()
    username = data.get("username")
    uid = data.get("uid")

    if not uid or not username:
        logger.error("UserDTO missing expected fields from Pi")
        raise HTTPException(status_code=401, detail="Invalid Pi user data")
    logger.info(f"Verified Pi user: {username} (UID: {uid})")
    # Return a dict containing user info, mimicking what your app expects
    return {"owner_id": uid, "username": username}

@router.get("/pi-auth/verify", summary="Verify Pi Network access token")
async def verify_pi_token(authorization: str = Header(None)):
    user = await verify_token(authorization)
    return {
        "message": "Pi token is valid",
        "username": user["username"],
        "uid": user["owner_id"]
    }
