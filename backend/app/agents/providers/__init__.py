"""
LLM Provider Package for Phase III

This package contains pluggable LLM provider implementations.
"""

from .base import LLMProvider
from .mock_provider import MockProvider

__all__ = [
    'LLMProvider',
    'MockProvider',
]

# Conditionally export OpenAIProvider if available
try:
    from .openai_provider import OpenAIProvider
    __all__.append('OpenAIProvider')
except ImportError:
    pass
