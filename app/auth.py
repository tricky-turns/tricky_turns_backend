import base64
import json
import logging
from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param

EXPECTED_AUDIENCE = "https://vercel.com/tricky-s-projects"
EXPECTED_ISSUER = "https://oidc.vercel.com/tricky-s-projects"

def verify_token(request: Request):
    authorization: str = request.headers.get("authorization")
    scheme, token = get_authorization_scheme_param(authorization)

    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

    try:
        # Safely decode the JWT header
        header_b64 = token.split(".")[0]
        padding = '=' * (-len(header_b64) % 4)
        header_bytes = base64.urlsafe_b64decode(header_b64 + padding)
        header = json.loads(header_bytes.decode("utf-8"))

        # Decode and verify the token using jose
        from jose import jwt
        key = get_public_key(header["kid"])
        payload = jwt.decode(
            token,
            key=jwt.construct_rsa_public_key(key),
            algorithms=["RS256"],
            audience=EXPECTED_AUDIENCE,
            issuer=EXPECTED_ISSUER
        )

        return payload

    except Exception as e:
        logging.exception("Token verification failed")
        raise HTTPException(status_code=401, detail="Invalid or malformed token")
