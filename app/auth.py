from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError

# This public key is provided by Pi Network and used to verify Pi login tokens
PI_AUTH_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE7ZfHb0o1McFSu/5zYKn2h1JHw3Bq
gacx0l1NxmxFzjjEqWyT2ejGL5v5do7Ooz/NQ2zvW9OnNUX65xgeIJJe9g==
-----END PUBLIC KEY-----"""

ALGORITHMS = ["ES256"]

security = HTTPBearer()

async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    credentials = await security(request)
    token = credentials.credentials
    print(f"🔐 Received Authorization header: {auth_header}")

    try:
        payload = jwt.decode(token, PI_AUTH_PUBLIC_KEY, algorithms=ALGORITHMS)
        print(f"✅ Token decoded successfully: {payload}")
        username = payload.get("user", {}).get("username")
        if not username:
            raise ValueError("Missing username")
        return { "username": username }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Pi token")