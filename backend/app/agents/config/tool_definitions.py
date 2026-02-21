"""
MCP Tool Definitions for Agent Configuration

This module defines the tool schemas that are passed to the AI agent.
These definitions allow the agent to understand what tools are available
and how to invoke them.

The schemas are compatible with Anthropic's tool use API format.
"""

from typing import List, Dict, Any


def get_mcp_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get tool definitions for MCP todo management tools — Phase V.

    Returns:
        List of tool definitions in Anthropic format
    """
    return [
        {
            "name": "create_todo",
            "description": "Create a new todo item. Supports Phase V fields: priority, tags, due_date, recurring_pattern.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Authenticated user ID"},
                    "title": {"type": "string", "description": "Task description"},
                    "completed": {"type": "boolean", "description": "Initial status (default false)"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Task priority"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for categorisation"},
                    "due_date": {"type": "string", "description": "ISO 8601 due date (e.g. 2026-03-01T00:00:00)"},
                    "recurring_pattern": {"type": "string", "enum": ["daily", "weekly", "monthly"], "description": "Recurrence schedule"},
                },
                "required": ["user_id", "title"],
            },
        },
        {
            "name": "list_todos",
            "description": "List todo items for the user with optional status filter.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Authenticated user ID"},
                    "completed": {"type": "boolean", "description": "Filter: true=completed, false=pending, omit=all"},
                },
                "required": ["user_id"],
            },
        },
        {
            "name": "search_todos",
            "description": "Phase V: Advanced search/filter/sort. Use when user wants to find tasks by keyword, priority, tag, or due date.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Authenticated user ID"},
                    "q": {"type": "string", "description": "Keyword to search in descriptions"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                    "tag": {"type": "string", "description": "Filter by tag"},
                    "is_complete": {"type": "boolean", "description": "Filter by completion status"},
                    "due_before": {"type": "string", "description": "ISO 8601 date — tasks due before this"},
                    "due_after": {"type": "string", "description": "ISO 8601 date — tasks due after this"},
                    "sort_by": {"type": "string", "enum": ["created_at", "updated_at", "due_date", "priority"]},
                    "sort_order": {"type": "string", "enum": ["asc", "desc"]},
                },
                "required": ["user_id"],
            },
        },
        {
            "name": "update_todo",
            "description": "Update an existing todo item. Supports Phase V partial updates (title, priority, tags, due_date, recurring).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Authenticated user ID"},
                    "todo_id": {"type": "integer", "description": "Task ID to update"},
                    "title": {"type": "string", "description": "New title"},
                    "completed": {"type": "boolean", "description": "New completion status"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "due_date": {"type": "string", "description": "ISO 8601 due date"},
                    "recurring_pattern": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                },
                "required": ["user_id", "todo_id"],
            },
        },
        {
            "name": "delete_todo",
            "description": "Delete a todo item permanently. Always confirm with user first.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Authenticated user ID"},
                    "todo_id": {"type": "integer", "description": "Task ID to delete"},
                },
                "required": ["user_id", "todo_id"],
            },
        },
        {
            "name": "get_todo",
            "description": "Get a specific todo item by ID.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Authenticated user ID"},
                    "todo_id": {"type": "integer", "description": "Task ID to retrieve"},
                },
                "required": ["user_id", "todo_id"],
            },
        },
        {
            "name": "get_overdue_todos",
            "description": "Phase V: Get all overdue tasks (past due_date, not completed).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "Authenticated user ID"},
                },
                "required": ["user_id"],
            },
        },
    ]


def get_tool_by_name(tool_name: str) -> Dict[str, Any]:
    """
    Get a specific tool definition by name.

    Args:
        tool_name: Name of the tool to retrieve

    Returns:
        Tool definition dict

    Raises:
        ValueError: If tool name not found
    """
    tools = get_mcp_tool_definitions()
    for tool in tools:
        if tool["name"] == tool_name:
            return tool
    raise ValueError(f"Tool not found: {tool_name}")


def validate_tool_call(tool_name: str, parameters: Dict[str, Any]) -> bool:
    """
    Validate that a tool call has required parameters.

    Args:
        tool_name: Name of the tool
        parameters: Parameters provided

    Returns:
        True if valid, False otherwise
    """
    try:
        tool_def = get_tool_by_name(tool_name)
        required_params = tool_def["input_schema"].get("required", [])

        for param in required_params:
            if param not in parameters:
                return False

        return True
    except ValueError:
        return False
