"""
Database — Engine, Session & Table Creation

One engine per process, one session per request.
The session is injected as a dependency via get_session().
"""

from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy import text

from app import crud
from app.config import get_settings
from app.models.hero import Hero
from app.models.user import User
from app.models.mission import Mission
from app.schemas.user import AdminCreate

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=False,
    connect_args={"check_same_thread": False}, 
)


def create_db_and_tables():
    """Create all tables. In production, use Alembic migrations instead."""
    SQLModel.metadata.create_all(engine)

def init_db(session: Session) -> None:
    """
    Initialize the database with:
      1. Create tables if they don't exist
      2. Create the first superuser if it doesn't exist
    """
    # Create tables if they don't exist
    try:
        # Test if user table exists
        session.exec(text("SELECT 1 FROM user LIMIT 1")).first()
        print("✅ Database tables already exist")
    except Exception:
        # Table doesn't exist, create it
        print("📦 Creating database tables...")
        create_db_and_tables()
        print("✅ Tables created successfully!")

        # Create superuser admin
        _create_superuser(session)
        

def _create_superuser(session:Session) -> None:
    """
    Create the first superuser if it doesn't exist.
    """
    if not settings.FIRST_SUPERUSER:
        print("⚠️  No FIRST_SUPERUSER configured, skipping superuser creation")
        return
    
    # Check if superuser already exists
    user = session.exec(
        select(User).where(User.username == settings.FIRST_SUPERUSER)
    ).first()

    if not user:
        print(f"👤 Creating superuser: {settings.FIRST_SUPERUSER}")
        user_in = AdminCreate(
            username=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
        )
        user = crud.create_user(session=session, user_create=user_in)
        print("✅ Superuser created successfully!")
    else:
        print(f"✅ Superuser already exists: {settings.FIRST_SUPERUSER}")
    
    return user

def get_session():
    """Yield a database session per request."""
    with Session(engine) as session:
        yield session