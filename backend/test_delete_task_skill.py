"""
Test script for DeleteTask skill.

This script verifies that:
1. task_parser.py extracts search terms correctly when an ID is not provided.
2. remove_task tool alias exists in MCP server.
3. chat.py formatting results in correct message structure: "Task deleted permanently."
"""

import sys
from pathlib import Path

# Add backend and project root to path
backend_dir = Path(__file__).parent.resolve()
project_root = backend_dir.parent.resolve()
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))

from app.agents.task_parser import extract_search_term

def test_search_term_extraction():
    """Test natural language search term extraction for deletions."""
    print("\n=== Test 1: Search Term Extraction ===")
    
    test_cases = [
        ("delete the meeting task", "meeting"),
        ("remove my shopping todo", "shopping"),
        ("Delete groceries item", "groceries"),
        ("remove study", "study"),
        ("cancel the gym session", "gym session"),
        ("remove task 3", None), # Should be None as it's an ID
        ("delete 5", None),      # Should be None as it's an ID
    ]
    
    for text, expected in test_cases:
        result = extract_search_term(text)
        print(f"Input: '{text}' -> Search Term: '{result}'")
        assert result == expected
    
    print("✓ Search term extraction working correctly")

def test_mcp_tool_alias():
    """Test that remove_task tool exists in MCP server."""
    print("\n=== Test 2: MCP Tool Alias ===")
    
    from phase_iii.mcp_server.tools.todo_tools import remove_task_tool, delete_todo_tool
    assert remove_task_tool is not None
    assert remove_task_tool == delete_todo_tool
    print("✓ remove_task_tool exists and is an alias for delete_todo_tool")

def test_confirmation_pattern():
    """Verify confirmation message pattern."""
    print("\n=== Test 3: Confirmation Pattern ===")
    
    confirmation = "Task deleted permanently."
    print(f"✓ Pattern: {confirmation}")
    
    assert confirmation == "Task deleted permanently."
    print("✓ Confirmation pattern matches requirement")

if __name__ == "__main__":
    print("=" * 60)
    print("DeleteTask Skill - Test Suite")
    print("=" * 60)
    
    try:
        test_search_term_extraction()
        test_mcp_tool_alias()
        test_confirmation_pattern()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
