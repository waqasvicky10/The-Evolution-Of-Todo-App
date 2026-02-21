"""
AI Agents Package — Phase V.

Consolidates all AI agent components:
    - TodoAgent: Main conversational agent
    - DeploymentAgent: DOKS deployment with P+Q+P
    - KafkaAgent: Event-driven Redpanda/Kafka with P+Q+P
    - DaprAgent: Dapr building blocks (Pub/Sub, State, Bindings, Secrets, Invoke)
    - AdvancedFeatureAgent: Phase V features (recurring, reminders, priorities, tags, search)
    - MasterPhaseVAgent: Top-level orchestrator coordinating all sub-agents
    - AgentConfig: Configuration management
    - System prompts & sub-agent prompts (Phase V)
    - Tool definitions: MCP tool schemas (Phase V — search, priority, tags, etc.)
    - Providers: Mock (Phase V intents), OpenAI, Qwen
    - Task parser: NLP utilities (Phase V — priority, tags, due_date, recurring)
    - User context: JWT-based user identity extraction
"""

from .agent import TodoAgent, create_agent
from .deployment_agent import DeploymentAgent
from .kafka_agent import KafkaAgent
from .dapr_agent import DaprAgent
from .advanced_feature_agent import AdvancedFeatureAgent
from .master_agent import MasterPhaseVAgent
from .config.agent_config import AgentConfig, get_agent_config
from .config.tool_definitions import get_mcp_tool_definitions, get_tool_by_name
from .prompts.system_prompt import get_system_prompt
from .agent_prompts import (
    TODO_AGENT_SYSTEM_PROMPT,
    USER_INFO_SUBAGENT_PROMPT,
    TASK_CRUD_SUBAGENT_PROMPT,
    CONVERSATION_MANAGER_SUBAGENT_PROMPT,
    DEPLOYMENT_AGENT_SYSTEM_PROMPT,
    DAPR_AGENT_SYSTEM_PROMPT,
    ADVANCED_FEATURE_AGENT_SYSTEM_PROMPT,
    MASTER_AGENT_SYSTEM_PROMPT,
)
from .task_parser import (
    parse_task_input,
    parse_list_status,
    extract_task_id,
    extract_search_term,
    parse_update_input,
    parse_search_query,
    extract_priority,
    extract_tags,
    extract_due_date_hint,
    extract_recurring,
    parse_advanced_task_input,
)
from .user_context import (
    get_user_context_from_token,
    get_user_context_from_credentials,
    format_user_greeting,
)

__all__ = [
    # Agents
    'TodoAgent',
    'create_agent',
    'DeploymentAgent',
    'KafkaAgent',
    'DaprAgent',
    'AdvancedFeatureAgent',
    'MasterPhaseVAgent',
    # Config
    'AgentConfig',
    'get_agent_config',
    'get_mcp_tool_definitions',
    'get_tool_by_name',
    'get_system_prompt',
    # Prompts
    'TODO_AGENT_SYSTEM_PROMPT',
    'USER_INFO_SUBAGENT_PROMPT',
    'TASK_CRUD_SUBAGENT_PROMPT',
    'CONVERSATION_MANAGER_SUBAGENT_PROMPT',
    'DEPLOYMENT_AGENT_SYSTEM_PROMPT',
    'DAPR_AGENT_SYSTEM_PROMPT',
    'ADVANCED_FEATURE_AGENT_SYSTEM_PROMPT',
    'MASTER_AGENT_SYSTEM_PROMPT',
    # Task parser (Phase V)
    'parse_task_input',
    'parse_list_status',
    'extract_task_id',
    'extract_search_term',
    'parse_update_input',
    'parse_search_query',
    'extract_priority',
    'extract_tags',
    'extract_due_date_hint',
    'extract_recurring',
    'parse_advanced_task_input',
    # User context
    'get_user_context_from_token',
    'get_user_context_from_credentials',
    'format_user_greeting',
]