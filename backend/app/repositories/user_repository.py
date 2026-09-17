from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from typing import Optional
import uuid


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        normalized = email.strip().lower()
        return self.db.query(User).filter(User.email == normalized).first()

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, name: str, email: str, password_hash: str, timezone: str = "UTC") -> User:
        normalized = email.strip().lower()
        user = User(name=name.strip(), email=normalized, password_hash=password_hash, timezone=timezone)
        self.db.add(user)
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise
