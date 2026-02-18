"""
Qwen LLM Provider for Phase III

This provider implements Qwen-based LLM calls using the OpenAI-compatible API.
"""

import logging
from typing import Any, Dict

from .openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

class QwenProvider(OpenAIProvider):
    """
    Qwen LLM provider using OpenAI-compatible API (e.g. DashScope).
    """
    
    def __init__(self, api_key: str, base_url: str, model_name: str, config: Any = None):
        """
        Initialize the Qwen Provider.
        
        Args:
            api_key: Qwen API key
            base_url: API Base URL (e.g. https://dashscope-intl.aliyuncs.com/compatible-mode/v1)
            model_name: Model name (e.g. qwen-plus)
            config: Optional configuration object
        """
        # Initialize parent (OpenAIProvider)
        # We need to manually initialize because OpenAIProvider's __init__ 
        # doesn't accept base_url, so we'll override the client creation.
        
        # Call parent init with dummy key if needed, or just rely on our override
        # But OpenAIProvider checks for openai package availability.
        super().__init__(api_key=api_key, config=config)
        
        # Override client with Qwen specific config
        try:
            import httpx
            from openai import OpenAI as OpenAIClient
            self.client = OpenAIClient(
                api_key=api_key,
                base_url=base_url,
                http_client=httpx.Client()
            )
            self.model = model_name
            logger.info(f"QwenProvider initialized with model: {self.model} at {base_url}")
        except ImportError:
            raise ImportError("openai and httpx packages are required.")

    def get_model_info(self) -> Dict[str, Any]:
        """Get Qwen provider info."""
        return {
            "model": self.model,
            "provider": "qwen",
            "capabilities": ["english", "urdu", "voice-ready", "tool-calling"]
        }
