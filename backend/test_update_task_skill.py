"""
Test script for UpdateTask skill.

This script verifies that:
1. task_parser.py extracts task IDs and new content correctly for updates.
2. update_task tool alias exists in MCP server.
"""

import sys
from pathlib import Path

# Add backend and project root to path
backend_dir = Path(__file__).parent.resolve()
project_root = backend_dir.parent.resolve()
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))

from app.agents.task_parser import parse_update_input

def test_update_parsing():
    """Test natural language update extraction."""
    print("\n=== Test 1: Update Parsing ===")
    
    test_cases = [
        ("Change task 2 to Buy milk and eggs", 2, "Buy milk and eggs"),
        ("update item 5: call the doctor", 5, "call the doctor"),
        ("edit #10 with clean the room", 10, "clean the room"),
        ("Change 123 to finish work", 123, "finish work"),
        ("Update task 15", 15, None), # Should still get ID but no content
    ]
    
    for text, exp_id, exp_content in test_cases:
        result = parse_update_input(text)
        print(f"Input: '{text}' -> ID: '{result['task_id']}', Content: '{result['new_content']}'")
        assert result['task_id'] == exp_id
        assert result['new_content'] == exp_content
    
    print("✓ Update parsing working correctly")

def test_mcp_tool_alias():
    """Test that update_task tool exists in MCP server."""
    print("\n=== Test 2: MCP Tool Alias ===")
    
    from phase_iii.mcp_server.tools.todo_tools import update_task_tool, update_todo_tool
    assert update_task_tool is not None
    assert update_task_tool == update_todo_tool
    print("✓ update_task_tool exists and is an alias for update_todo_tool")

if __name__ == "__main__":
    print("=" * 60)
    print("UpdateTask Skill - Test Suite")
    print("=" * 60)
    
    try:
        test_update_parsing()
        test_mcp_tool_alias()
        
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
