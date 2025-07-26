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
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header[7:]
    try:
        decoded = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"], audience=None)  # audience=None if you're not validating it
        print("DECODED PAYLOAD:", decoded)
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print("JWT decode failed:", e)
        raise HTTPException(status_code=403, detail="Invalid token")
