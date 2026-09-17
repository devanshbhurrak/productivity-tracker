from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, settings.auth_secret, algorithm=settings.jwt_algorithm)
    return encoded


# Simple in-memory revoked token store (for logout)
_revoked_tokens: set[str] = set()

def revoke_token(token: str) -> None:
    _revoked_tokens.add(token)

def is_token_revoked(token: str) -> bool:
    return token in _revoked_tokens

def decode_access_token(token: str) -> Optional[dict]:
    if is_token_revoked(token):
        return None
    try:
        payload = jwt.decode(token, settings.auth_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None
