from typing import Optional

from sqlalchemy.orm import Session

from .models import User, UserCreate, SessionLocal


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()
    
    def create(self, user_data: UserCreate) -> User:
        user = User(
            telegram_id=user_data.telegram_id,
            language=user_data.language,
            custom_instruction=user_data.custom_instruction
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_or_create(self, telegram_id: int) -> User:
        user = self.get_by_telegram_id(telegram_id)
        if not user:
            user = self.create(UserCreate(telegram_id=telegram_id))
        return user
    
    def update_language(self, telegram_id: int, language: str) -> User:
        """Update user's language preference."""
        user = self.get_or_create(telegram_id)
        user.language = language
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_custom_instruction(self, telegram_id: int, custom_instruction: str) -> User:
        """Update user's custom instruction."""
        user = self.get_or_create(telegram_id)
        user.custom_instruction = custom_instruction
        self.db.commit()
        self.db.refresh(user)
        return user


def get_user_repo() -> UserRepository:
    """Get a UserRepository instance with a fresh database session."""
    db = SessionLocal()
    return UserRepository(db) 