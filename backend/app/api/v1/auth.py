from fastapi import APIRouter, Depends, Response, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import get_settings
from app.schemas.auth import RegisterRequest, LoginRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(name=payload.name, email=payload.email, password=payload.password, timezone=payload.timezone)
    return user


@router.post("/login", status_code=status.HTTP_200_OK, summary="Authenticate a user")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    service = AuthService(db)
    user, token = service.login(email=payload.email, password=payload.password)
    # Set HttpOnly cookie
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure if not settings.is_testing else False,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )
    # Also return token in body for convenience/API clients
    return {"access_token": token, "token_type": "bearer", "user": UserResponse.model_validate(user).model_dump()}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Log out current user")
def logout(request: Request, response: Response, current_user: User = Depends(get_current_user)):
    # Revoke token if present (header or cookie)
    from app.core.security import revoke_token
    from app.core.config import get_settings
    settings_local = get_settings()
    token = None
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        token = auth[7:]
    if not token:
        token = request.cookies.get(settings_local.cookie_name)
    # Also check via bearer_scheme fallback: try to get from request
    if token:
        revoke_token(token)
    response.delete_cookie(key=settings_local.cookie_name, path="/")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse, summary="Return authenticated user")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
