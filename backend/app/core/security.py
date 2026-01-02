"""
Security utilities for password hashing and JWT token management.

This module provides secure password hashing using bcrypt and JWT token
generation/validation for authentication.
"""

import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string (bcrypt hash, ~60 characters)

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> print(len(hashed))  # ~60 characters
        60
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database

    Returns:
        True if password matches hash, False otherwise

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> verify_password("SecurePass123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: int) -> str:
    """
    Generate JWT access token for authenticated user.

    Args:
        user_id: User ID to encode in token

    Returns:
        JWT token string (valid for 15 minutes)

    Example:
        >>> token = create_access_token(user_id=1)
        >>> # Token can be used in Authorization: Bearer <token>
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """
    Generate JWT refresh token for token renewal.

    Args:
        user_id: User ID to encode in token

    Returns:
        JWT refresh token string (valid for 7 days)

    Example:
        >>> refresh_token = create_refresh_token(user_id=1)
        >>> # Use this token to get new access token
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> dict:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Token payload dict containing user_id, exp, and type

    Raises:
        ValueError: If token is invalid or expired

    Example:
        >>> token = create_access_token(user_id=1)
        >>> payload = verify_token(token)
        >>> print(payload["user_id"])
        1
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")
