"""
FastAPI dependency injection functions.

This module provides dependency functions for database sessions
and user authentication.
"""

from sqlmodel import Session, select
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_session
from app.core.security import verify_token
from app.models.user import User


# HTTP Bearer token security scheme
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Provides a SQLModel session that is automatically closed after use.
    Use this dependency in FastAPI endpoints to get database access.

    Yields:
        Database session

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    yield from get_session()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency function to get currently authenticated user.

    Extracts and validates JWT token from Authorization header,
    verifies the token, and retrieves the user from database.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        Authenticated user object

    Raises:
        HTTPException 401: If token is invalid, expired, or user not found

    Example:
        @app.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.email}
    """
    try:
        # Extract token from Authorization header
        token = credentials.credentials

        # Verify and decode token
        payload = verify_token(token)

        # Extract user_id from payload
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

    except ValueError:
        # Token verification failed (invalid or expired)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Query user from database
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
