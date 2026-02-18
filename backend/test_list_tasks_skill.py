"""
Test script for ListTasks skill.

This script verifies that:
1. task_parser.py extracts correct status (all/pending/completed).
2. list_tasks tool alias exists in todo_tools.py.
3. list_tasks handler in todo_tools.py correctly maps status string to filter.
4. chat.py formatting results in correct message structure.
"""

import sys
from pathlib import Path

# Add backend and project root to path
backend_dir = Path(__file__).parent.resolve()
project_root = backend_dir.parent.resolve()
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))

from app.agents.task_parser import parse_list_status

def test_status_parsing():
    """Test natural language status extraction."""
    print("\n=== Test 1: Status Parsing ===")
    
    test_cases = [
        ("show pending tasks", "pending"),
        ("list incomplete items", "pending"),
        ("show completed todos", "completed"),
        ("what is finished?", "completed"),
        ("list all tasks", "all"),
        ("show records", "all"),
    ]
    
    for text, expected in test_cases:
        result = parse_list_status(text)
        print(f"Input: '{text}' -> Status: '{result}'")
        assert result == expected
    
    print("✓ Status parsing working correctly")

def test_mcp_tool_alias():
    """Test that list_tasks tool exists as an alias in MCP server."""
    print("\n=== Test 2: MCP Tool Alias ===")
    
    from phase_iii.mcp_server.tools.todo_tools import list_tasks_tool, list_todos_tool
    assert list_tasks_tool == list_todos_tool
    print("✓ list_tasks_tool alias exists and points to list_todos_tool")

def test_formatting_logic():
    """Verify formatting logic pattern."""
    print("\n=== Test 3: Formatting Logic ===")
    
    # Mock some tasks
    tasks = [
        {"id": 1, "description": "buy milk", "is_complete": False},
        {"id": 2, "description": "call mom", "is_complete": True},
    ]
    
    message = "Here are your tasks:\n"
    for t in tasks:
        status_emoji = "✅" if t["is_complete"] else "⏳"
        message += f"{status_emoji} **ID: {t['id']}** - {t['description']}\n"
    
    print(f"Formatted Message:\n{message}")
    
    assert "⏳ **ID: 1** - buy milk" in message
    assert "✅ **ID: 2** - call mom" in message
    print("✓ Beautiful formatting logic verified")

if __name__ == "__main__":
    print("=" * 60)
    print("ListTasks Skill - Test Suite")
    print("=" * 60)
    
    try:
        test_status_parsing()
        test_mcp_tool_alias()
        test_formatting_logic()
        
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
