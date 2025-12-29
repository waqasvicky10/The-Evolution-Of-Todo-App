"""
Task data model for Phase I Todo application.

This module defines the Task entity and validation functions.
"""

from dataclasses import dataclass


@dataclass
class Task:
    """
    Represents a single todo task.

    Attributes:
        id: Unique positive integer identifier
        description: Task description (1-500 characters)
        is_complete: Task completion status (default False)
    """

    id: int
    description: str
    is_complete: bool = False

    def __post_init__(self) -> None:
        """Validate task fields after initialization."""
        if self.id < 1:
            raise ValueError("Task ID must be positive")
        if not self.description or len(self.description) > 500:
            raise ValueError("Description must be 1-500 characters")


def validate_description(description: str) -> bool:
    """
    Validate task description meets constraints.

    Args:
        description: Task description to validate

    Returns:
        True if valid, False otherwise
    """
    if not description:
        return False
    if len(description) > 500:
        return False
    return True
