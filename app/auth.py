import os
import base64
import json
import logging
import requests
from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param

PUBLIC_KEY_ENDPOINT = "https://oidc.vercel.app/.well-known/jwks.json"
EXPECTED_ISSUER = "https://oidc.vercel.app/tricky-s-projects"
EXPECTED_AUDIENCE = "https://vercel.com/tricky-s-projects"

def get_public_key(kid: str):
    keys = requests.get(PUBLIC_KEY_ENDPOINT).json()["keys"]
    for key in keys:
        if key["kid"] == kid:
            return key
    raise Exception("Public key not found")

def verify_token(request: Request):
    authorization: str = request.headers.get("authorization")
    scheme, token = get_authorization_scheme_param(authorization)

    if not authorization or scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    try:
        header_b64 = token.split(".")[0]
        header = json.loads(base64.urlsafe_b64decode(header_b64 + "=="))
        key = get_public_key(header["kid"])

        from jose import jwt

        payload = jwt.decode(
            token,
            key=jwt.construct_rsa_public_key(key),
            algorithms=["RS256"],
            audience=EXPECTED_AUDIENCE,
            issuer=EXPECTED_ISSUER,
        )

        return payload
    except Exception as e:
        logging.exception("Token verification failed")
        raise HTTPException(status_code=401, detail="Invalid token")