"""
Agent Configuration for Phase III

This module defines configuration parameters for the AI agent.
Configuration is loaded from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentConfig:
    """
    Configuration for the Todo AI Agent.

    Attributes:
        model: Model identifier (OpenAI or mock)
        temperature: Response randomness (0.0-1.0)
        max_tokens: Maximum response length
        timeout: API request timeout in seconds
    """

    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 30

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """
        Create configuration from environment variables.

        Environment variables:
            - AGENT_MODEL: Model to use (default: gpt-4o-mini)
            - AGENT_TEMPERATURE: Response temperature
            - AGENT_MAX_TOKENS: Max response tokens
            - AGENT_TIMEOUT: API timeout seconds

        Returns:
            AgentConfig with values from environment or defaults
        """
        return cls(
            model=os.getenv("AGENT_MODEL", cls.model),
            temperature=float(os.getenv("AGENT_TEMPERATURE", cls.temperature)),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", cls.max_tokens)),
            timeout=int(os.getenv("AGENT_TIMEOUT", cls.timeout))
        )

    def to_dict(self):
        """Convert config to dictionary."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout
        }


def get_agent_config() -> AgentConfig:
    """
    Get agent configuration from environment.

    Returns:
        AgentConfig instance
    """
    return AgentConfig.from_env()
