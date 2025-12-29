"""
Unit tests for operations module.

Tests all CRUD operations and task management functions.
"""

import pytest
from phase_i.models import Task
from phase_i import operations


# ============================================================================
# get_next_id tests
# ============================================================================


def test_get_next_id_empty_list():
    """Test get_next_id returns 1 for empty list."""
    tasks = []
    assert operations.get_next_id(tasks) == 1


def test_get_next_id_single_task():
    """Test get_next_id returns 2 when list has task with id=1."""
    tasks = [Task(id=1, description="Task 1")]
    assert operations.get_next_id(tasks) == 2


def test_get_next_id_multiple_tasks():
    """Test get_next_id returns max+1 for multiple tasks."""
    tasks = [
        Task(id=1, description="Task 1"),
        Task(id=2, description="Task 2"),
        Task(id=3, description="Task 3"),
    ]
    assert operations.get_next_id(tasks) == 4


def test_get_next_id_with_gaps():
    """Test get_next_id handles gaps correctly."""
    tasks = [Task(id=1, description="Task 1"), Task(id=3, description="Task 3")]
    assert operations.get_next_id(tasks) == 4


# ============================================================================
# add_task tests
# ============================================================================


def test_add_task_valid():
    """Test successfully adding task with valid description."""
    tasks = []
    success, message, task = operations.add_task(tasks, "Buy groceries")

    assert success is True
    assert "Task added with ID 1" in message
    assert len(tasks) == 1
    assert tasks[0].description == "Buy groceries"
    assert tasks[0].id == 1
    assert task is not None
    assert task.description == "Buy groceries"


def test_add_task_empty_description():
    """Test add_task returns error for empty string."""
    tasks = []
    success, message, task = operations.add_task(tasks, "")

    assert success is False
    assert "Task description cannot be empty" in message
    assert task is None
    assert len(tasks) == 0


def test_add_task_whitespace_only():
    """Test add_task returns error for whitespace-only."""
    tasks = []
    success, message, task = operations.add_task(tasks, "   ")

    assert success is False
    assert "Task description cannot be empty" in message
    assert task is None


def test_add_task_description_too_long():
    """Test add_task returns error for 501 characters."""
    tasks = []
    long_desc = "a" * 501
    success, message, task = operations.add_task(tasks, long_desc)

    assert success is False
    assert "Task description too long" in message
    assert task is None


def test_add_task_description_exactly_500():
    """Test add_task succeeds with 500 characters."""
    tasks = []
    desc_500 = "a" * 500
    success, message, task = operations.add_task(tasks, desc_500)

    assert success is True
    assert task is not None
    assert len(tasks[0].description) == 500


def test_add_task_strips_whitespace():
    """Test add_task strips leading/trailing whitespace."""
    tasks = []
    success, message, task = operations.add_task(tasks, "  Buy groceries  ")

    assert success is True
    assert tasks[0].description == "Buy groceries"


def test_add_task_multiple_tasks():
    """Test IDs increment correctly."""
    tasks = []
    operations.add_task(tasks, "Task 1")
    operations.add_task(tasks, "Task 2")
    operations.add_task(tasks, "Task 3")

    assert len(tasks) == 3
    assert tasks[0].id == 1
    assert tasks[1].id == 2
    assert tasks[2].id == 3


def test_add_task_returns_created_task():
    """Test add_task returns the created task object."""
    tasks = []
    success, message, task = operations.add_task(tasks, "Test task")

    assert task is not None
    assert task.id == 1
    assert task.description == "Test task"
    assert task.is_complete is False


# ============================================================================
# get_all_tasks tests
# ============================================================================


def test_get_all_tasks_empty():
    """Test get_all_tasks returns empty list."""
    tasks = []
    result = operations.get_all_tasks(tasks)
    assert result == []


def test_get_all_tasks_multiple():
    """Test get_all_tasks returns all tasks."""
    tasks = [
        Task(id=1, description="Task 1"),
        Task(id=2, description="Task 2"),
    ]
    result = operations.get_all_tasks(tasks)
    assert len(result) == 2
    assert result is tasks  # Same reference


# ============================================================================
# get_task_by_id tests
# ============================================================================


def test_get_task_by_id_found():
    """Test get_task_by_id returns task when exists."""
    tasks = [
        Task(id=1, description="Task 1"),
        Task(id=2, description="Task 2"),
    ]
    task = operations.get_task_by_id(tasks, 2)
    assert task is not None
    assert task.id == 2
    assert task.description == "Task 2"


def test_get_task_by_id_not_found():
    """Test get_task_by_id returns None when not exists."""
    tasks = [Task(id=1, description="Task 1")]
    task = operations.get_task_by_id(tasks, 99)
    assert task is None


def test_get_task_by_id_empty_list():
    """Test get_task_by_id returns None for empty list."""
    tasks = []
    task = operations.get_task_by_id(tasks, 1)
    assert task is None


# ============================================================================
# update_task tests
# ============================================================================


def test_update_task_valid():
    """Test successfully updating description."""
    tasks = [Task(id=1, description="Original")]
    success, message = operations.update_task(tasks, 1, "Updated")

    assert success is True
    assert "Task 1 updated" in message
    assert tasks[0].description == "Updated"


def test_update_task_not_found():
    """Test update_task returns error for invalid ID."""
    tasks = [Task(id=1, description="Task 1")]
    success, message = operations.update_task(tasks, 99, "New desc")

    assert success is False
    assert "Task with ID 99 not found" in message


def test_update_task_empty_description():
    """Test update_task returns error for empty string."""
    tasks = [Task(id=1, description="Original")]
    success, message = operations.update_task(tasks, 1, "")

    assert success is False
    assert "Task description cannot be empty" in message
    assert tasks[0].description == "Original"  # Unchanged


def test_update_task_too_long():
    """Test update_task returns error for 501 characters."""
    tasks = [Task(id=1, description="Original")]
    long_desc = "a" * 501
    success, message = operations.update_task(tasks, 1, long_desc)

    assert success is False
    assert "Task description too long" in message


def test_update_task_strips_whitespace():
    """Test update_task strips whitespace."""
    tasks = [Task(id=1, description="Original")]
    success, message = operations.update_task(tasks, 1, "  Updated  ")

    assert success is True
    assert tasks[0].description == "Updated"


# ============================================================================
# delete_task tests
# ============================================================================


def test_delete_task_valid():
    """Test successfully removing task."""
    tasks = [
        Task(id=1, description="Task 1"),
        Task(id=2, description="Task 2"),
    ]
    success, message = operations.delete_task(tasks, 1)

    assert success is True
    assert "Task 1 deleted" in message
    assert len(tasks) == 1
    assert tasks[0].id == 2


def test_delete_task_not_found():
    """Test delete_task returns error for invalid ID."""
    tasks = [Task(id=1, description="Task 1")]
    success, message = operations.delete_task(tasks, 99)

    assert success is False
    assert "Task with ID 99 not found" in message
    assert len(tasks) == 1  # Unchanged


def test_delete_task_list_modified():
    """Test delete_task verifies list length decreases."""
    tasks = [
        Task(id=1, description="Task 1"),
        Task(id=2, description="Task 2"),
        Task(id=3, description="Task 3"),
    ]
    initial_len = len(tasks)
    operations.delete_task(tasks, 2)

    assert len(tasks) == initial_len - 1
    assert operations.get_task_by_id(tasks, 2) is None


# ============================================================================
# mark_complete tests
# ============================================================================


def test_mark_complete_valid():
    """Test successfully marking incomplete task complete."""
    tasks = [Task(id=1, description="Task 1", is_complete=False)]
    success, message = operations.mark_complete(tasks, 1)

    assert success is True
    assert "Task 1 marked as complete" in message
    assert tasks[0].is_complete is True


def test_mark_complete_not_found():
    """Test mark_complete returns error for invalid ID."""
    tasks = [Task(id=1, description="Task 1")]
    success, message = operations.mark_complete(tasks, 99)

    assert success is False
    assert "Task with ID 99 not found" in message


def test_mark_complete_already_complete():
    """Test mark_complete returns info message for already complete."""
    tasks = [Task(id=1, description="Task 1", is_complete=True)]
    success, message = operations.mark_complete(tasks, 1)

    assert success is True
    assert "already marked complete" in message


def test_mark_complete_status_changed():
    """Test mark_complete verifies is_complete = True."""
    tasks = [Task(id=1, description="Task 1", is_complete=False)]
    operations.mark_complete(tasks, 1)
    assert tasks[0].is_complete is True


# ============================================================================
# mark_incomplete tests
# ============================================================================


def test_mark_incomplete_valid():
    """Test successfully marking complete task incomplete."""
    tasks = [Task(id=1, description="Task 1", is_complete=True)]
    success, message = operations.mark_incomplete(tasks, 1)

    assert success is True
    assert "Task 1 marked as incomplete" in message
    assert tasks[0].is_complete is False


def test_mark_incomplete_not_found():
    """Test mark_incomplete returns error for invalid ID."""
    tasks = [Task(id=1, description="Task 1")]
    success, message = operations.mark_incomplete(tasks, 99)

    assert success is False
    assert "Task with ID 99 not found" in message


def test_mark_incomplete_already_incomplete():
    """Test mark_incomplete returns info message for already incomplete."""
    tasks = [Task(id=1, description="Task 1", is_complete=False)]
    success, message = operations.mark_incomplete(tasks, 1)

    assert success is True
    assert "already marked incomplete" in message


def test_mark_incomplete_status_changed():
    """Test mark_incomplete verifies is_complete = False."""
    tasks = [Task(id=1, description="Task 1", is_complete=True)]
    operations.mark_incomplete(tasks, 1)
    assert tasks[0].is_complete is False
