from fastapi import Header, HTTPException

from app.core.config import settings


def require_auth(authorization: str | None = Header(default=None)) -> bool:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    if token != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid token")

    return True
