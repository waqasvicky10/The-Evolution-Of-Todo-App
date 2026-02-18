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
    Get tool definitions for MCP todo management tools.

    Returns:
        List of tool definitions in Anthropic format
    """
    return [
        {
            "name": "create_todo",
            "description": "Create a new todo item for the user. Use this when the user wants to add a task, create a reminder, or add something to their todo list.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the authenticated user (automatically provided)"
                    },
                    "title": {
                        "type": "string",
                        "description": "The title or description of the todo item"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Initial completion status (default: false)"
                    }
                },
                "required": ["user_id", "title"]
            }
        },
        {
            "name": "list_todos",
            "description": "List all todo items for the user. Use this when the user wants to see their tasks, check their list, or view what they need to do.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the authenticated user (automatically provided)"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Optional filter: true for completed todos, false for incomplete todos, omit for all todos"
                    }
                },
                "required": ["user_id"]
            }
        },
        {
            "name": "update_todo",
            "description": "Update an existing todo item. Use this when the user wants to change, modify, or update a task's title or details.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the authenticated user (automatically provided)"
                    },
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the todo item to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the todo item (optional, only if changing)"
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "New completion status (optional, only if changing)"
                    }
                },
                "required": ["user_id", "todo_id"]
            }
        },
        {
            "name": "delete_todo",
            "description": "Delete a todo item permanently. Use this when the user wants to remove or delete a task. IMPORTANT: Always confirm with the user before calling this tool.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the authenticated user (automatically provided)"
                    },
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the todo item to delete"
                    }
                },
                "required": ["user_id", "todo_id"]
            }
        },
        {
            "name": "get_todo",
            "description": "Get a specific todo item by ID. Use this when you need to retrieve details about a particular todo.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "ID of the authenticated user (automatically provided)"
                    },
                    "todo_id": {
                        "type": "integer",
                        "description": "ID of the todo item to retrieve"
                    }
                },
                "required": ["user_id", "todo_id"]
            }
        }
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
