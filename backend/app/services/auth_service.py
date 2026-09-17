from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.exceptions.base import ConflictException, UnauthorizedException, BadRequestException
from app.models.user import User


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, name: str, email: str, password: str, timezone: str = "UTC") -> User:
        # Check duplicate
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ConflictException(code="EMAIL_ALREADY_EXISTS", message="Email already registered")
        pw_hash = hash_password(password)
        try:
            user = self.user_repo.create(name=name, email=email, password_hash=pw_hash, timezone=timezone)
            return user
        except IntegrityError:
            raise ConflictException(code="EMAIL_ALREADY_EXISTS", message="Email already registered")

    def login(self, email: str, password: str) -> tuple[User, str]:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedException(code="INVALID_CREDENTIALS", message="Invalid email or password")
        token = create_access_token({"sub": str(user.id), "email": user.email})
        return user, token

    def get_user_by_id(self, user_id: str) -> User | None:
        import uuid
        try:
            uid = uuid.UUID(user_id)
        except Exception:
            return None
        return self.user_repo.get_by_id(uid)
