"""
Business logic and CRUD operations for Phase I Todo application.

This module implements all task operations including add, update, delete,
and status management.
"""

from typing import List, Tuple, Optional
from phase_i.models import Task, validate_description


def get_next_id(tasks: List[Task]) -> int:
    """
    Generate next available task ID.

    Args:
        tasks: Current list of tasks

    Returns:
        Next sequential ID (1 if list empty, max_id + 1 otherwise)
    """
    if not tasks:
        return 1
    return max(task.id for task in tasks) + 1


def add_task(
    tasks: List[Task], description: str
) -> Tuple[bool, str, Optional[Task]]:
    """
    Add new task to list.

    Args:
        tasks: Task list (modified in-place)
        description: Task description

    Returns:
        Tuple of (success, message, created_task)
        - (True, success_message, task) on success
        - (False, error_message, None) on failure
    """
    # Validate description
    if not description.strip():
        return (False, "Task description cannot be empty", None)

    if len(description) > 500:
        return (False, "Task description too long (max 500 characters)", None)

    # Generate ID and create task
    next_id = get_next_id(tasks)
    new_task = Task(id=next_id, description=description.strip(), is_complete=False)
    tasks.append(new_task)

    return (True, f'Task added with ID {next_id}: "{description.strip()}"', new_task)


def get_all_tasks(tasks: List[Task]) -> List[Task]:
    """
    Get all tasks.

    Args:
        tasks: Task list

    Returns:
        List of all tasks (same reference, not a copy)
    """
    return tasks


def get_task_by_id(tasks: List[Task], task_id: int) -> Optional[Task]:
    """
    Find task by ID.

    Args:
        tasks: Task list
        task_id: ID to search for

    Returns:
        Task if found, None otherwise
    """
    return next((task for task in tasks if task.id == task_id), None)


def update_task(tasks: List[Task], task_id: int, new_description: str) -> Tuple[bool, str]:
    """
    Update task description.

    Args:
        tasks: Task list
        task_id: ID of task to update
        new_description: New description text

    Returns:
        Tuple of (success, message)
    """
    task = get_task_by_id(tasks, task_id)
    if not task:
        return (False, f"Task with ID {task_id} not found")

    if not new_description.strip():
        return (False, "Task description cannot be empty")

    if len(new_description) > 500:
        return (False, "Task description too long (max 500 characters)")

    task.description = new_description.strip()
    return (True, f'Task {task_id} updated to "{new_description.strip()}"')


def delete_task(tasks: List[Task], task_id: int) -> Tuple[bool, str]:
    """
    Delete task from list.

    Args:
        tasks: Task list (modified in-place)
        task_id: ID of task to delete

    Returns:
        Tuple of (success, message)
    """
    task = get_task_by_id(tasks, task_id)
    if not task:
        return (False, f"Task with ID {task_id} not found")

    tasks.remove(task)
    return (True, f"Task {task_id} deleted")


def mark_complete(tasks: List[Task], task_id: int) -> Tuple[bool, str]:
    """
    Mark task as complete.

    Args:
        tasks: Task list
        task_id: ID of task to mark complete

    Returns:
        Tuple of (success, message)
    """
    task = get_task_by_id(tasks, task_id)
    if not task:
        return (False, f"Task with ID {task_id} not found")

    if task.is_complete:
        return (True, f"Info: Task {task_id} is already marked complete")

    task.is_complete = True
    return (True, f"Task {task_id} marked as complete")


def mark_incomplete(tasks: List[Task], task_id: int) -> Tuple[bool, str]:
    """
    Mark task as incomplete.

    Args:
        tasks: Task list
        task_id: ID of task to mark incomplete

    Returns:
        Tuple of (success, message)
    """
    task = get_task_by_id(tasks, task_id)
    if not task:
        return (False, f"Task with ID {task_id} not found")

    if not task.is_complete:
        return (True, f"Info: Task {task_id} is already marked incomplete")

    task.is_complete = False
    return (True, f"Task {task_id} marked as incomplete")
