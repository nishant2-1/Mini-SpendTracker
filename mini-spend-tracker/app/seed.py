from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User
from app.security import hash_password, verify_password


def ensure_demo_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.username == settings.demo_username))
    if user is None:
        user = User(
            username=settings.demo_username,
            password_hash=hash_password(settings.demo_password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    if not verify_password(settings.demo_password, user.password_hash):
        user.password_hash = hash_password(settings.demo_password)
        db.commit()
        db.refresh(user)
    return user
