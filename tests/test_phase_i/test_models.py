"""
Unit tests for Task model.

Tests Task creation, validation, and default values.
"""

import pytest
from phase_i.models import Task, validate_description


def test_task_creation_valid():
    """Test creating a task with valid data."""
    task = Task(id=1, description="Buy groceries")
    assert task.id == 1
    assert task.description == "Buy groceries"
    assert task.is_complete is False


def test_task_creation_with_defaults():
    """Test that is_complete defaults to False."""
    task = Task(id=1, description="Test task")
    assert task.is_complete is False


def test_task_invalid_id_zero():
    """Test that id=0 raises ValueError."""
    with pytest.raises(ValueError, match="Task ID must be positive"):
        Task(id=0, description="Test")


def test_task_invalid_id_negative():
    """Test that negative id raises ValueError."""
    with pytest.raises(ValueError, match="Task ID must be positive"):
        Task(id=-1, description="Test")


def test_task_empty_description():
    """Test that empty description raises ValueError."""
    with pytest.raises(ValueError, match="Description must be 1-500 characters"):
        Task(id=1, description="")


def test_task_description_too_long():
    """Test that 501 character description raises ValueError."""
    long_desc = "a" * 501
    with pytest.raises(ValueError, match="Description must be 1-500 characters"):
        Task(id=1, description=long_desc)


def test_task_description_exactly_500():
    """Test that 500 character description is valid."""
    desc_500 = "a" * 500
    task = Task(id=1, description=desc_500)
    assert len(task.description) == 500


def test_validate_description_valid():
    """Test validate_description returns True for valid description."""
    assert validate_description("Valid task description") is True


def test_validate_description_empty():
    """Test validate_description returns False for empty string."""
    assert validate_description("") is False


def test_validate_description_too_long():
    """Test validate_description returns False for 501 characters."""
    long_desc = "a" * 501
    assert validate_description(long_desc) is False


def test_task_is_complete_true():
    """Test creating a task with is_complete=True."""
    task = Task(id=1, description="Completed task", is_complete=True)
    assert task.is_complete is True
