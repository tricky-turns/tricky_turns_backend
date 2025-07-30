# app/auth.py

from fastapi import APIRouter, HTTPException, Header
import httpx
import logging

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
    logger.info(f"Verified Pi user: {username}")
    return {"username": username}

@router.get("/pi-auth/verify", summary="Verify Pi Network access token")
async def verify_pi_token(authorization: str = Header(None)):
    user = await verify_token(authorization)
    return {
        "message": "Pi token is valid",
        "username": user["username"]
    }
