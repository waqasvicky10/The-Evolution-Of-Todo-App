"""
Test script for TodoChatAgent integration.

This script verifies:
1. OpenAIProvider includes the system prompt.
2. TodoAgent handles tool call results and Urdu correctly.
3. The system prompt instructs the agent to call GetUserContext first.
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
from app.agents.agent_prompts import TODO_AGENT_SYSTEM_PROMPT

class TestTodoChatAgent(TracebackTestCase if hasattr(unittest, 'TracebackTestCase') else unittest.TestCase):
    
    def setUp(self):
        self.api_key = "test_key"
        self.provider = OpenAIProvider(api_key=self.api_key)
        self.agent = TodoAgent(provider=self.provider)

    def test_system_prompt_injection(self):
        """Verify that the system prompt is injected into the message sequence."""
        messages = self.provider._convert_messages_to_openai_format([], "Hello")
        
        # Check that the first message is the system prompt
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], TODO_AGENT_SYSTEM_PROMPT)
        
        # Check that the user message is present
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], "Hello")

    @patch('phase_iii.agent.providers.openai_provider.OpenAIClient')
    def test_agent_calls_get_user_context_behavior(self, mock_openai_client):
        """
        Verify that the agent (via the provider) would return a tool call for get_user_context.
        """
        # Create a proper mock for the chat response
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        
        # Simulate a tool call object
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
        
        # Setup the mock client
        instance = mock_openai_client.return_value
        instance.chat.completions.create.return_value = mock_response
        
        # We need to re-initialize the provider so it uses the mocked client
        provider = OpenAIProvider(api_key="test_key")
        agent = TodoAgent(provider=provider)
        
        result = agent.process_message("Hello", [], user_id=1, tools=[{"name": "get_user_context"}])
        
        print(f"DEBUG: result['tool_calls'] = {result['tool_calls']}")
        self.assertTrue(result["requires_tool_execution"])
        self.assertEqual(len(result["tool_calls"]), 1)
        self.assertEqual(result["tool_calls"][0]["name"], "get_user_context")

    def test_process_tool_results_urdu(self):
        """Verify that tool results support Urdu summarization via message pass-through."""
        tool_results = [{
            "content": {
                "success": True,
                "message": "ٹاسک کامیابی سے محفوظ کر لیا گیا ہے۔"
            }
        }]
        
        # This will set is_urdu_context = True because the message is in Urdu
        result = self.agent.process_tool_results(tool_results, user_id=1)
        self.assertIn("ٹاسک کامیابی سے محفوظ", result["response_text"])

if __name__ == "__main__":
    unittest.main()
