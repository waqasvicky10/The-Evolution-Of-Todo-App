"""
Authentication API routes.

This module provides endpoints for user registration, login, logout,
and token refresh operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest, UserResponse
from app.services.user_service import create_user, authenticate_user
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.config import settings
from app.api.deps import get_db, get_current_user
from app.models.user import User


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    Register a new user account.

    Creates a new user with email and password. Password is hashed before
    storage. Email must be unique.

    Args:
        request: Registration request with email, password, and password_confirmation
        db: Database session

    Returns:
        Created user data (without password)

    Raises:
        400: Validation error (invalid email, weak password, password mismatch)
        409: Email already exists
        500: Server error

    Example:
        POST /api/auth/register
        {
            "email": "user@example.com",
            "password": "SecurePass123!",
            "password_confirmation": "SecurePass123!"
        }

        Response 201:
        {
            "id": 1,
            "email": "user@example.com",
            "created_at": "2026-01-01T12:00:00Z"
        }
    """
    user = create_user(db, email=request.email, password=request.password)
    # Convert datetime to ISO string for response
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat()
    }


@router.post("/login", response_model=TokenResponse)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and return JWT tokens.

    Authenticates user credentials and generates access and refresh tokens.

    Args:
        request: Login request with email and password
        db: Database session

    Returns:
        Access token, refresh token, and expiration time

    Raises:
        401: Invalid credentials (email or password)
        500: Server error

    Example:
        POST /api/auth/login
        {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }

        Response 200:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 900
        }
    """
    # Authenticate user
    user = authenticate_user(db, email=request.email, password=request.password)

    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Return tokens
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user.

    Token invalidation happens client-side by discarding tokens.
    This endpoint confirms the user is authenticated before logout.

    Args:
        current_user: Currently authenticated user

    Returns:
        Success message

    Example:
        POST /api/auth/logout
        Headers: Authorization: Bearer <access_token>

        Response 200:
        {
            "message": "Logged out successfully"
        }
    """
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.

    Validates refresh token and generates new access token.
    Returns the same refresh token (not regenerated).

    Args:
        request: Refresh token request

    Returns:
        New access token with same refresh token

    Raises:
        401: Invalid or expired refresh token
        401: Invalid token type (not a refresh token)

    Example:
        POST /api/auth/refresh
        {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }

        Response 200:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 900
        }
    """
    try:
        # Verify refresh token
        payload = verify_token(request.refresh_token)

        # Check token type is "refresh"
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # Extract user_id
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Generate new access token
        new_access_token = create_access_token(user_id)

        # Return new access token with same refresh token
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=request.refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except ValueError:
        # Token verification failed (invalid or expired)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
