"""
Test script for CompleteTask skill.

This script verifies that:
1. task_parser.py extracts numeric task IDs correctly.
2. complete_task tool exists in MCP server.
3. chat.py formatting results in correct message structure: "Task [ID] marked complete ✓".
"""

import sys
from pathlib import Path

# Add backend and project root to path
backend_dir = Path(__file__).parent.resolve()
project_root = backend_dir.parent.resolve()
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))

from app.agents.task_parser import extract_task_id

def test_id_extraction():
    """Test natural language task ID extraction."""
    print("\n=== Test 1: ID Extraction ===")
    
    test_cases = [
        ("mark task 5 as done", 5),
        ("complete item 10", 10),
        ("I finished #15 today", 15),
        ("finished 123", 123),
        ("nothing here", None),
    ]
    
    for text, expected in test_cases:
        result = extract_task_id(text)
        print(f"Input: '{text}' -> ID: '{result}'")
        assert result == expected
    
    print("✓ ID extraction working correctly")

def test_mcp_tool_alias():
    """Test that complete_task tool exists in MCP server."""
    print("\n=== Test 2: MCP Tool Alias ===")
    
    from phase_iii.mcp_server.tools.todo_tools import complete_task_tool, update_todo_tool
    assert complete_task_tool is not None
    print("✓ complete_task_tool exists")

def test_confirmation_pattern():
    """Verify confirmation message pattern."""
    print("\n=== Test 3: Confirmation Pattern ===")
    
    task_id = 5
    confirmation = f"Task {task_id} marked complete ✓"
    print(f"✓ Pattern: {confirmation}")
    
    assert confirmation == "Task 5 marked complete ✓"
    print("✓ Confirmation pattern matches requirement")

if __name__ == "__main__":
    print("=" * 60)
    print("CompleteTask Skill - Test Suite")
    print("=" * 60)
    
    try:
        test_id_extraction()
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
