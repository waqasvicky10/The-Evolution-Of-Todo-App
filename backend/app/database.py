"""
Database connection and session management.

Provides SQLModel engine, session factory, and database initialization.
"""

from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from app.config import settings
import re


# Debug: Print DATABASE_URL (with password masked for security)
def mask_password(url: str) -> str:
    """Mask password in connection string for safe logging."""
    # Pattern: postgresql://user:password@host/db
    return re.sub(r'(://[^:]+:)([^@]+)(@)', r'\1****\3', url)

if settings.ENVIRONMENT == "development":
    print(f"[Database] DATABASE_URL = {mask_password(settings.DATABASE_URL)}")
    print(f"[Database] Database type: {'PostgreSQL' if settings.DATABASE_URL.startswith('postgresql') else 'SQLite'}")


# Create database engine
# Support both PostgreSQL and SQLite (for local development without PostgreSQL)
# Add connection timeout and pool settings for better reliability
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # PostgreSQL connection args - optimized for Neon
    connect_args["connect_timeout"] = 5  # Reduced to 5 seconds
    # sslmode is already in connection string, don't duplicate

# Optimize engine settings for faster connections
import os
_is_serverless = os.environ.get("VERCEL", "") == "1" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME", "")

if _is_serverless:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=2,
        pool_timeout=10,
        pool_recycle=300,
        connect_args=connect_args,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=5,
        pool_timeout=10,
        pool_recycle=3600,
        connect_args=connect_args,
        execution_options={"autocommit": False}
    )


def _ensure_phase_v_columns() -> None:
    """
    Add missing Phase V columns to tasks table if they don't exist.
    Works with SQLite and PostgreSQL. Idempotent.
    """
    from sqlalchemy import inspect, text

    with engine.connect() as conn:
        insp = inspect(conn)
        if "tasks" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("tasks")}
        is_sqlite = "sqlite" in str(engine.url)
        # Column name -> (SQLite type, PG type)
        to_add = {
            "priority": ("TEXT", "VARCHAR(20)"),
            "tags": ("TEXT", "VARCHAR(500)"),
            "due_date": ("TEXT", "TIMESTAMP"),
            "reminder_at": ("TEXT", "TIMESTAMP"),
            "recurring_pattern": ("TEXT", "VARCHAR(50)"),
            "category": ("TEXT", "VARCHAR(50)"),
            "estimated_duration": ("TEXT", "VARCHAR(50)"),
            "ai_tags": ("TEXT", "VARCHAR(500)"),
            "ai_suggestions": ("TEXT", "VARCHAR(1000)"),
        }
        for col_name, (sqlite_t, pg_t) in to_add.items():
            if col_name not in cols:
                t = sqlite_t if is_sqlite else pg_t
                conn.execute(text(f'ALTER TABLE tasks ADD COLUMN "{col_name}" {t}'))
                conn.commit()


def init_db() -> None:
    """
    Create all database tables and ensure Phase V columns exist.

    This function creates all tables defined in SQLModel models,
    then adds any missing Phase V columns to existing tables.
    """
    SQLModel.metadata.create_all(engine)
    _ensure_phase_v_columns()


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
