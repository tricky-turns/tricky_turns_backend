import base64
import json
import logging

from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param

# Set these when you upgrade to OIDC
EXPECTED_AUDIENCE = "https://vercel.com/tricky-s-projects"  # or your app's OIDC aud
EXPECTED_ISSUER = "https://oidc.vercel.com/tricky-s-projects"  # or whatever Pi provides

def get_public_key(kid: str):
    # Placeholder — fill in later when OIDC is enabled
    raise NotImplementedError("Public key lookup not implemented")

def verify_token(request: Request):
    authorization: str = request.headers.get("authorization")
    scheme, token = get_authorization_scheme_param(authorization)

    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )

    # Check for JWT (OIDC) format: eyJ...
    if token.startswith("eyJ"):
        try:
            header_b64 = token.split(".")[0]
            padding = '=' * (-len(header_b64) % 4)
            header_bytes = base64.urlsafe_b64decode(header_b64 + padding)
            header = json.loads(header_bytes.decode("utf-8"))

            from jose import jwt
            key = get_public_key(header["kid"])

            payload = jwt.decode(
                token,
                key=jwt.construct_rsa_public_key(key),
                algorithms=["RS256"],
                audience=EXPECTED_AUDIENCE,
                issuer=EXPECTED_ISSUER
            )

            return {
                "owner_id": payload.get("sub"),
                "username": payload.get("username")
            }

        except Exception as e:
            logging.exception("❌ JWT verification failed")
            raise HTTPException(status_code=401, detail="Invalid JWT token")

    # Fallback: Legacy Pi token
    print(f"⚠️ Legacy Pi token used: {token[:10]}... (not verifiable)")
    return {
        "owner_id": token,  # Use the raw token string as a unique user ID
        "username": None    # Frontend must send username separately
    }
