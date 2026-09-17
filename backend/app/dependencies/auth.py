from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.config import get_settings
from app.models.user import User
from app.exceptions.base import UnauthorizedException
import uuid

# Optional HTTP Bearer for fallback
bearer_scheme = HTTPBearer(auto_error=False)
settings = get_settings()


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = None
    # Prefer Authorization header if provided (explicit bearer overrides cookie)
    if credentials:
        token = credentials.credentials
    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth[7:]
    # Fall back to cookie
    if not token:
        token = request.cookies.get(settings.cookie_name)

    if not token:
        raise UnauthorizedException(message="Authentication required")

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedException(message="Invalid or expired token")

    user_id = payload["sub"]
    try:
        uid = uuid.UUID(user_id)
    except Exception:
        raise UnauthorizedException(message="Invalid token subject")

    user = db.query(User).filter(User.id == uid).first()
    if not user:
        raise UnauthorizedException(message="User not found")
    return user
