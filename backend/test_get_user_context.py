"""
Test script for GetUserContext skill.

This script verifies that:
1. JWT tokens include email and name in the payload
2. get_user_context_from_token() correctly extracts user context
3. User context includes user_id, email, and name fields
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.security import create_access_token, verify_token
from app.agents.user_context import get_user_context_from_token, format_user_greeting


def test_jwt_with_email():
    """Test JWT token creation with email."""
    print("\n=== Test 1: JWT Token with Email ===")
    
    # Create token with email
    token = create_access_token(user_id=1, email="waqas@example.com")
    print(f"✓ Token created: {token[:50]}...")
    
    # Verify token payload
    payload = verify_token(token)
    print(f"✓ Token payload: {payload}")
    
    # Check email is in payload
    assert "email" in payload, "Email not found in token payload!"
    assert payload["email"] == "waqas@example.com", "Email mismatch!"
    assert payload["user_id"] == 1, "User ID mismatch!"
    print("✓ Email and user_id correctly encoded in token")
    

def test_jwt_with_email_and_name():
    """Test JWT token creation with email and name."""
    print("\n=== Test 2: JWT Token with Email and Name ===")
    
    # Create token with email and name
    token = create_access_token(user_id=2, email="ali@example.com", name="Ali Khan")
    print(f"✓ Token created: {token[:50]}...")
    
    # Verify token payload
    payload = verify_token(token)
    print(f"✓ Token payload: {payload}")
    
    # Check all fields
    assert payload["user_id"] == 2, "User ID mismatch!"
    assert payload["email"] == "ali@example.com", "Email mismatch!"
    assert payload["name"] == "Ali Khan", "Name mismatch!"
    print("✓ User ID, email, and name correctly encoded in token")


def test_get_user_context():
    """Test get_user_context_from_token function."""
    print("\n=== Test 3: GetUserContext Skill Function ===")
    
    # Create token
    token = create_access_token(user_id=3, email="sara@example.com", name="Sara Ahmed")
    
    # Extract user context using the skill
    context = get_user_context_from_token(token)
    print(f"✓ User context extracted: {context}")
    
    # Verify context structure
    assert "user_id" in context, "user_id not in context!"
    assert "email" in context, "email not in context!"
    assert "name" in context, "name not in context!"
    
    # Verify values
    assert context["user_id"] == 3, "User ID mismatch in context!"
    assert context["email"] == "sara@example.com", "Email mismatch in context!"
    assert context["name"] == "Sara Ahmed", "Name mismatch in context!"
    print("✓ GetUserContext skill working correctly")


def test_get_user_context_without_name():
    """Test get_user_context_from_token when name is not provided."""
    print("\n=== Test 4: GetUserContext without Name ===")
    
    # Create token without name
    token = create_access_token(user_id=4, email="test@example.com")
    
    # Extract user context
    context = get_user_context_from_token(token)
    print(f"✓ User context extracted: {context}")
    
    # Verify context
    assert context["user_id"] == 4, "User ID mismatch!"
    assert context["email"] == "test@example.com", "Email mismatch!"
    assert context["name"] is None, "Name should be None!"
    print("✓ GetUserContext handles missing name correctly")


def test_format_greeting():
    """Test format_user_greeting helper function."""
    print("\n=== Test 5: Format User Greeting ===")
    
    # Test with name
    context1 = {"user_id": 1, "email": "waqas@example.com", "name": "Waqas"}
    greeting1_en = format_user_greeting(context1, language="en")
    greeting1_ur = format_user_greeting(context1, language="ur")
    
    print(f"✓ English greeting: {greeting1_en}")
    print(f"✓ Urdu greeting: {greeting1_ur}")
    
    assert "Waqas" in greeting1_en, "Name not in English greeting!"
    assert "Waqas" in greeting1_ur, "Name not in Urdu greeting!"
    
    # Test without name (should use email prefix)
    context2 = {"user_id": 2, "email": "ali@example.com", "name": None}
    greeting2 = format_user_greeting(context2, language="en")
    
    print(f"✓ Greeting without name: {greeting2}")
    assert "ali" in greeting2, "Email prefix not used in greeting!"
    
    print("✓ Greeting formatting works correctly")


def test_skill_pattern():
    """Demonstrate the GetUserContext skill pattern."""
    print("\n=== Test 6: GetUserContext Skill Pattern ===")
    print("Pattern demonstration:")
    print("1. Extract JWT token from Authorization: Bearer <token> header")
    
    # Simulate token from header
    authorization_header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    token_from_header = authorization_header.replace("Bearer ", "")
    print(f"   Token extracted: {token_from_header[:30]}...")
    
    # Create actual token for demo
    actual_token = create_access_token(user_id=5, email="demo@example.com", name="Demo User")
    
    print("2. JWT decoded using Better Auth secret (via verify_token)")
    payload = verify_token(actual_token)
    print(f"   Payload: {payload}")
    
    print("3. Return: {\"user_id\": \"...\", \"email\": \"...\", \"name\": \"...\"}")
    context = get_user_context_from_token(actual_token)
    print(f"   Context: {context}")
    
    print("✓ Skill pattern demonstrated successfully")


if __name__ == "__main__":
    print("=" * 60)
    print("GetUserContext Skill - Test Suite")
    print("=" * 60)
    
    try:
        test_jwt_with_email()
        test_jwt_with_email_and_name()
        test_get_user_context()
        test_get_user_context_without_name()
        test_format_greeting()
        test_skill_pattern()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nGetUserContext Skill is ready to use!")
        print("\nUsage in FastAPI routes:")
        print("  from app.api.deps import get_user_context")
        print("  ")
        print("  @app.get('/endpoint')")
        print("  def my_endpoint(context: dict = Depends(get_user_context)):")
        print("      user_id = context['user_id']")
        print("      email = context['email']")
        print("      name = context['name']")
        print("      return {'message': f'Hello {email}!'}")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
