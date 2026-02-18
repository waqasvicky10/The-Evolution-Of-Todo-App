"""
Test script for ConversationManagerSubagent skill.

This script verifies that:
1. ConversationManagerSubagent prompt facilitates multi-turn logic.
2. The agent correctly resolves context (e.g., "it") using the provided history.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend and project root to path
backend_dir = Path(__file__).parent.resolve()
project_root = backend_dir.parent.resolve()
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))

from phase_iii.agent.agent import TodoAgent
from phase_iii.agent.providers.openai_provider import OpenAIProvider
from app.agents.agent_prompts import CONVERSATION_MANAGER_SUBAGENT_PROMPT

class TestConversationManagerSubagent(unittest.TestCase):
    
    def setUp(self):
        self.api_key = "mock_key"
        self.provider = OpenAIProvider(api_key=self.api_key)
        self.agent = TodoAgent(provider=self.provider)

    @patch('phase_iii.agent.providers.openai_provider.OpenAIClient')
    def test_context_resolution_logic(self, mock_openai_client):
        """Verify that the agent resolves "it" based on history."""
        # Setup mock for the client instance
        instance = mock_openai_client.return_value
        
        # Setup mock for the chat response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        # Simulate a tool call to complete_task with ID 5
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_context_123"
        mock_tool_call.function.name = "complete_task"
        mock_tool_call.function.arguments = '{"user_id": 1, "todo_id": 5}'
        
        mock_message.content = ""
        mock_message.tool_calls = [mock_tool_call]
        mock_choice.message = mock_message
        mock_choice.finish_reason = "tool_calls"
        mock_response.choices = [mock_choice]
        mock_response.model_dump_json.return_value = "{}"
        
        instance.chat.completions.create.return_value = mock_response
        
        # Re-initialize provider to use the mock
        provider = OpenAIProvider(api_key="mock_key")
        agent = TodoAgent(provider=provider)
        
        # History showing a task was just added
        history = [
            {"role": "user", "content": "Add task Buy milk"},
            {"role": "assistant", "content": "Task added successfully. (ID: 5)"}
        ]
        
        result = agent.process_message(
            "Actually, complete it", 
            history, 
            user_id=1, 
            tools=[{"name": "complete_task"}],
            system_prompt=CONVERSATION_MANAGER_SUBAGENT_PROMPT
        )
        
        self.assertTrue(result["requires_tool_execution"])
        self.assertEqual(result["tool_calls"][0]["name"], "complete_task")
        self.assertEqual(result["tool_calls"][0]["input"]["todo_id"], 5)

if __name__ == "__main__":
    unittest.main()
