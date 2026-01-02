"""
Authentication request and response schemas.

Pydantic models for user registration, login, and token management.
"""

from pydantic import BaseModel, EmailStr, constr, field_validator
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    """
    User registration request schema.

    Validates email format, password strength, and password confirmation match.
    """

    email: EmailStr
    password: constr(min_length=8, max_length=100)
    password_confirmation: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets strength requirements.

        Requirements:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character (!@#$%^&*)

        Args:
            v: Password to validate

        Returns:
            Password if valid

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain an uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain a lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a number")
        if not any(c in "!@#$%^&*" for c in v):
            raise ValueError("Password must contain a special character")
        return v

    @field_validator("password_confirmation")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """
        Validate password confirmation matches password.

        Args:
            v: Password confirmation
            info: Validation info containing other field values

        Returns:
            Password confirmation if matches

        Raises:
            ValueError: If passwords don't match
        """
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    """
    User login request schema.

    Simple email and password validation for authentication.
    """

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    Token response schema.

    Returned after successful login or token refresh.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires


class RefreshTokenRequest(BaseModel):
    """
    Refresh token request schema.

    Used to request a new access token using a valid refresh token.
    """

    refresh_token: str


class UserResponse(BaseModel):
    """
    User response schema.

    Returns user data without sensitive information (no password).
    """

    id: int
    email: str
    created_at: str  # ISO format string

    class Config:
        from_attributes = True  # Allows creation from SQLModel objects
