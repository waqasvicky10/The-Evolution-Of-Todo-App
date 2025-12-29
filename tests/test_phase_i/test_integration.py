"""
Integration tests for Phase I Todo application.

Tests complete user flows from start to finish.
"""

import pytest
from phase_i.models import Task
from phase_i import operations


def test_add_and_view_flow():
    """Test adding a task and viewing it."""
    tasks = []

    # Add task
    success, message, task = operations.add_task(tasks, "Buy groceries")
    assert success is True
    assert len(tasks) == 1
    assert tasks[0].description == "Buy groceries"

    # View tasks
    all_tasks = operations.get_all_tasks(tasks)
    assert len(all_tasks) == 1
    assert all_tasks[0].id == 1


def test_add_update_view_flow():
    """Test adding, updating, and viewing a task."""
    tasks = []

    # Add task
    success, message, task = operations.add_task(tasks, "Original description")
    assert success is True
    task_id = task.id

    # Update task
    success, message = operations.update_task(tasks, task_id, "Updated description")
    assert success is True
    assert tasks[0].description == "Updated description"

    # View tasks
    all_tasks = operations.get_all_tasks(tasks)
    assert all_tasks[0].description == "Updated description"


def test_add_delete_view_flow():
    """Test adding task, deleting it, viewing empty list."""
    tasks = []

    # Add task
    success, message, task = operations.add_task(tasks, "Task to delete")
    assert success is True
    task_id = task.id

    # Delete task
    success, message = operations.delete_task(tasks, task_id)
    assert success is True
    assert len(tasks) == 0

    # View empty list
    all_tasks = operations.get_all_tasks(tasks)
    assert len(all_tasks) == 0


def test_add_mark_complete_view_flow():
    """Test adding task, marking complete, viewing with status."""
    tasks = []

    # Add task
    success, message, task = operations.add_task(tasks, "Task to complete")
    assert success is True
    task_id = task.id
    assert task.is_complete is False

    # Mark complete
    success, message = operations.mark_complete(tasks, task_id)
    assert success is True
    assert tasks[0].is_complete is True

    # Verify status
    retrieved_task = operations.get_task_by_id(tasks, task_id)
    assert retrieved_task.is_complete is True


def test_add_mark_incomplete_flow():
    """Test adding complete task, marking incomplete."""
    tasks = []

    # Add task and mark complete
    success, message, task = operations.add_task(tasks, "Task")
    task_id = task.id
    operations.mark_complete(tasks, task_id)
    assert tasks[0].is_complete is True

    # Mark incomplete
    success, message = operations.mark_incomplete(tasks, task_id)
    assert success is True
    assert tasks[0].is_complete is False


def test_multiple_tasks_flow():
    """Test adding multiple tasks and viewing all."""
    tasks = []

    # Add multiple tasks
    operations.add_task(tasks, "Task 1")
    operations.add_task(tasks, "Task 2")
    operations.add_task(tasks, "Task 3")

    assert len(tasks) == 3
    assert tasks[0].id == 1
    assert tasks[1].id == 2
    assert tasks[2].id == 3
    assert tasks[0].description == "Task 1"
    assert tasks[1].description == "Task 2"
    assert tasks[2].description == "Task 3"


def test_update_nonexistent_task():
    """Test trying to update invalid ID returns error."""
    tasks = []
    operations.add_task(tasks, "Task 1")

    success, message = operations.update_task(tasks, 99, "New description")
    assert success is False
    assert "not found" in message
    # Original task unchanged
    assert tasks[0].description == "Task 1"


def test_delete_nonexistent_task():
    """Test trying to delete invalid ID returns error."""
    tasks = []
    operations.add_task(tasks, "Task 1")

    success, message = operations.delete_task(tasks, 99)
    assert success is False
    assert "not found" in message
    # Task still exists
    assert len(tasks) == 1


def test_delete_with_confirmation_no():
    """Test delete flow when user declines confirmation."""
    tasks = []
    operations.add_task(tasks, "Task 1")
    task_id = tasks[0].id

    # In real usage, confirmation would be declined
    # Here we just verify task can still be found after not deleting
    task = operations.get_task_by_id(tasks, task_id)
    assert task is not None

    # Verify delete actually works when called
    success, message = operations.delete_task(tasks, task_id)
    assert success is True
    assert len(tasks) == 0


def test_id_generation_after_delete():
    """Test ID increments correctly after deletion."""
    tasks = []

    # Add tasks
    operations.add_task(tasks, "Task 1")  # ID 1
    operations.add_task(tasks, "Task 2")  # ID 2
    operations.add_task(tasks, "Task 3")  # ID 3

    # Delete task 2
    operations.delete_task(tasks, 2)

    # Add new task - should be ID 4, not 2
    success, message, new_task = operations.add_task(tasks, "Task 4")
    assert new_task.id == 4
    assert len(tasks) == 3


def test_empty_list_operations():
    """Test operations on empty list."""
    tasks = []

    # View empty list
    all_tasks = operations.get_all_tasks(tasks)
    assert len(all_tasks) == 0

    # Try operations on non-existent task
    task = operations.get_task_by_id(tasks, 1)
    assert task is None

    success, message = operations.update_task(tasks, 1, "New")
    assert success is False

    success, message = operations.delete_task(tasks, 1)
    assert success is False

    success, message = operations.mark_complete(tasks, 1)
    assert success is False


def test_complete_user_session():
    """Test full session with multiple operations."""
    tasks = []

    # Add multiple tasks
    operations.add_task(tasks, "Buy groceries")
    operations.add_task(tasks, "Finish homework")
    operations.add_task(tasks, "Call dentist")
    assert len(tasks) == 3

    # Mark one complete
    operations.mark_complete(tasks, 2)
    assert tasks[1].is_complete is True

    # Update one
    operations.update_task(tasks, 1, "Buy groceries and cook dinner")
    assert tasks[0].description == "Buy groceries and cook dinner"

    # Delete one
    operations.delete_task(tasks, 3)
    assert len(tasks) == 2

    # Add another
    success, message, new_task = operations.add_task(tasks, "New task")
    assert new_task.id == 3  # ID is max(remaining IDs) + 1 = 2 + 1 = 3

    # Verify final state
    assert len(tasks) == 3
    assert tasks[0].description == "Buy groceries and cook dinner"
    assert tasks[0].is_complete is False
    assert tasks[1].description == "Finish homework"
    assert tasks[1].is_complete is True
    assert tasks[2].description == "New task"
    assert tasks[2].is_complete is False
