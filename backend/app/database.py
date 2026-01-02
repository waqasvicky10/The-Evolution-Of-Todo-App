"""
Database connection and session management.

Provides SQLModel engine, session factory, and database initialization.
"""

from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from app.config import settings


# Create database engine
# Support both PostgreSQL and SQLite (for local development without PostgreSQL)
engine = create_engine(
    settings.DATABASE_URL,
    echo=True if settings.ENVIRONMENT == "development" else False,
    pool_pre_ping=True,  # Verify connections before using
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)


def init_db() -> None:
    """
    Create all database tables.

    This function creates all tables defined in SQLModel models.
    In production, use Alembic migrations instead.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields:
        Database session that will be automatically closed after use.

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_session)):
            items = db.query(Item).all()
            return items
    """
    with Session(engine) as session:
        yield session
