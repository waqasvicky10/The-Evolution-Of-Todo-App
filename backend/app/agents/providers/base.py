"""
Base LLM Provider Interface

Defines the interface that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All providers must implement the process_message method
    to handle user messages and generate tool calls.
    """
    
    @abstractmethod
    def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_id: int,
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and return agent response with tool calls.
        
        Args:
            user_message: The user's message
            conversation_history: Previous messages in the conversation
            user_id: ID of the user
            tools: Available tools for the agent to use
            
        Returns:
            Dict with:
                - response_text: Text response from the agent
                - tool_calls: List of tool calls to execute
                - requires_tool_execution: Whether tool calls need execution
                - stop_reason: Reason for stopping
                - language: Detected language (en/ur)
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model/provider.
        
        Returns:
            Dict with model and provider information
        """
        pass
