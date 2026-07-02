from sqlmodel import Session

from app.models.user import User
from app.schemas.user import AdminCreate, UserCreate
from app.security import hash_password


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """
    Create a normal user via registration.
    Users are NOT admins by default.
    """
    db_obj = User(
        username=user_create.username,
        hashed_password=hash_password(user_create.password),
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def create_admin_user(*, session: Session, user_create: AdminCreate) -> User:
    """Create the first superuser/admin on startup."""
    db_obj = User(
        username= user_create.username,
        hashed_password= hash_password(user_create.password),
        is_admin=True,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj