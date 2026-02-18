"""
Test script for UserInfoSubagent skill.

This script verifies that:
1. OpenAIProvider uses the custom system prompt when provided.
2. UserInfoSubagent prompt enforces the correct response pattern.
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
from app.agents.agent_prompts import USER_INFO_SUBAGENT_PROMPT

class TestUserInfoSubagent(unittest.TestCase):
    
    def setUp(self):
        self.api_key = "test_key"
        self.provider = OpenAIProvider(api_key=self.api_key)
        self.agent = TodoAgent(provider=self.provider)

    def test_custom_system_prompt_injection(self):
        """Verify that a custom system prompt can be injected."""
        custom_prompt = "You are a user info reporter."
        messages = self.provider._convert_messages_to_openai_format([], "Who am I?", system_prompt=custom_prompt)
        
        # Check that the first message is the custom system prompt
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], custom_prompt)

    @patch('phase_iii.agent.providers.openai_provider.OpenAIClient')
    def test_user_info_subagent_responses(self, mock_openai_client):
        """Verify that the agent uses the UserInfoSubagent prompt logic."""
        # Setup mock for the client instance
        instance = mock_openai_client.return_value
        
        # Setup mock for the chat response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        # Simulate a tool call to get_user_context
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "get_user_context"
        mock_tool_call.function.arguments = '{"user_id": 1}'
        
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
        
        # Test with UserInfoSubagent prompt
        result = agent.process_message(
            "Who am I?", 
            [], 
            user_id=1, 
            tools=[{"name": "get_user_context"}],
            system_prompt=USER_INFO_SUBAGENT_PROMPT
        )
        
        self.assertTrue(result["requires_tool_execution"])
        self.assertEqual(result["tool_calls"][0]["name"], "get_user_context")

    def test_summarization_pattern(self):
        """Verify that the agent correctly summarizes the tool result into the required pattern."""
        tool_results = [{
            "content": {
                "success": True,
                "email": "waqas@example.com",
                "message": "User context retrieved successfully."
            }
        }]
        
        # This will test the new logic in process_tool_results
        result = self.agent.process_tool_results(tool_results, user_id=1)
        self.assertEqual(result["response_text"], "You are logged in as waqas@example.com")

    def test_summarization_pattern_urdu(self):
        """Verify that the agent correctly summarizes the tool result in Urdu."""
        tool_results = [{
            "content": {
                "success": True,
                "email": "waqas@example.com",
                "message": "صارف کا ڈیٹا مل گیا۔" # Urdu message trigger
            }
        }]
        
        result = self.agent.process_tool_results(tool_results, user_id=1)
        self.assertEqual(result["response_text"], "آپ waqas@example.com کے طور پر لاگ ان ہیں۔")

if __name__ == "__main__":
    unittest.main()
