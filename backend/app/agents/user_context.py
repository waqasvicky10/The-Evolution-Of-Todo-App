"""
User context extraction utilities.

This module provides utilities to extract user context (user_id, email, name)
from JWT tokens for chatbot personalization and other features.
"""

from typing import Dict, Optional, Any
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import verify_token


def get_user_context_from_token(token: str) -> Dict[str, Any]:
    """
    Extract user context from JWT token.
    
    This is the core skill function that decodes a JWT token and extracts
    user information including user_id, email, and name (if available).
    
    Args:
        token: JWT token string from Authorization header
        
    Returns:
        Dictionary containing:
        - user_id: int - User's unique identifier
        - email: str | None - User's email address (if available in token)
        - name: str | None - User's name (if available in token)
        
    Raises:
        ValueError: If token is invalid or expired
        
    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> context = get_user_context_from_token(token)
        >>> print(context)
        {'user_id': 1, 'email': 'user@example.com', 'name': None}
        
    Pattern (as per skill requirement):
        1. Token is passed from Authorization: Bearer <token> header
        2. JWT is decoded using Better Auth secret (via verify_token)
        3. Returns user_id, email, and name from the payload
    """
    # Verify and decode the token
    payload = verify_token(token)
    
    # Extract user context from payload
    user_context = {
        "user_id": payload.get("user_id"),
        "email": payload.get("email"),
        "name": payload.get("name")
    }
    
    # Validate that we at least have a user_id
    if not user_context["user_id"]:
        raise ValueError("Token payload missing user_id")
    
    return user_context


def get_user_context_from_credentials(
    credentials: HTTPAuthorizationCredentials
) -> Dict[str, Any]:
    """
    Extract user context from FastAPI HTTPAuthorizationCredentials.
    
    Convenience wrapper for get_user_context_from_token that works
    directly with FastAPI's HTTPBearer security scheme.
    
    Args:
        credentials: HTTPAuthorizationCredentials from Depends(security)
        
    Returns:
        Dictionary containing user_id, email, and name
        
    Raises:
        ValueError: If token is invalid or expired
        
    Example:
        >>> from fastapi import Depends
        >>> from fastapi.security import HTTPBearer
        >>> 
        >>> security = HTTPBearer()
        >>> 
        >>> @app.get("/profile")
        >>> def get_profile(credentials = Depends(security)):
        >>>     context = get_user_context_from_credentials(credentials)
        >>>     return {"message": f"Hello {context['email']}!"}
    """
    token = credentials.credentials
    return get_user_context_from_token(token)


def format_user_greeting(user_context: Dict[str, Any], language: str = "en") -> str:
    """
    Format a personalized greeting based on user context.
    
    Helper function to generate personalized greetings for chatbot responses.
    
    Args:
        user_context: User context dict from get_user_context_from_token
        language: Language code ("en" for English, "ur" for Urdu)
        
    Returns:
        Personalized greeting string
        
    Example:
        >>> context = {"user_id": 1, "email": "waqas@example.com", "name": "Waqas"}
        >>> greeting = format_user_greeting(context, language="en")
        >>> print(greeting)
        "Hello Waqas!"
        
        >>> context = {"user_id": 1, "email": "waqas@example.com", "name": None}
        >>> greeting = format_user_greeting(context, language="ur")
        >>> print(greeting)
        "السلام علیکم waqas@example.com!"
    """
    # Get display name (prefer name, fallback to email prefix)
    display_name = user_context.get("name")
    if not display_name and user_context.get("email"):
        # Extract name from email (before @)
        display_name = user_context["email"].split("@")[0]
    elif not display_name:
        display_name = f"User #{user_context['user_id']}"
    
    # Format greeting based on language
    if language == "ur":
        return f"السلام علیکم {display_name}!"
    else:
        return f"Hello {display_name}!"
