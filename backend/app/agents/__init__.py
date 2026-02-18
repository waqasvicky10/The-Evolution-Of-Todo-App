"""
AI Agents Package for Phase III & IV

This package consolidates all AI agent components:
    - TodoAgent: Main agent class
    - AgentConfig: Configuration management
    - System prompts & sub-agent prompts
    - Tool definitions: MCP tool schemas
    - Providers: Mock, OpenAI, Qwen
    - Task parser: NLP utilities for task extraction
    - User context: JWT-based user identity extraction
"""

from .agent import TodoAgent, create_agent
from .config.agent_config import AgentConfig, get_agent_config
from .config.tool_definitions import get_mcp_tool_definitions, get_tool_by_name
from .prompts.system_prompt import get_system_prompt
from .agent_prompts import (
    TODO_AGENT_SYSTEM_PROMPT,
    USER_INFO_SUBAGENT_PROMPT,
    TASK_CRUD_SUBAGENT_PROMPT,
    CONVERSATION_MANAGER_SUBAGENT_PROMPT,
)
from .task_parser import (
    parse_task_input,
    parse_list_status,
    extract_task_id,
    extract_search_term,
    parse_update_input,
    parse_search_query,
)
from .user_context import (
    get_user_context_from_token,
    get_user_context_from_credentials,
    format_user_greeting,
)

__all__ = [
    'TodoAgent',
    'create_agent',
    'AgentConfig',
    'get_agent_config',
    'get_mcp_tool_definitions',
    'get_tool_by_name',
    'get_system_prompt',
    'TODO_AGENT_SYSTEM_PROMPT',
    'USER_INFO_SUBAGENT_PROMPT',
    'TASK_CRUD_SUBAGENT_PROMPT',
    'CONVERSATION_MANAGER_SUBAGENT_PROMPT',
    'parse_task_input',
    'parse_list_status',
    'extract_task_id',
    'extract_search_term',
    'parse_update_input',
    'parse_search_query',
    'get_user_context_from_token',
    'get_user_context_from_credentials',
    'format_user_greeting',
]