
"""
Task service for CRUD operations with user isolation — Phase V.

Supports advanced features: priority, tags, due dates, recurring tasks,
reminders, full-text search, filtering, and sorting.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlmodel import Session, select, col
from fastapi import HTTPException, status

from app.models.task import Task

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def get_user_tasks(
    db: Session,
    user_id: int,
    completed: Optional[bool] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Task]:
    """Get tasks for a user with basic filters (backward-compatible)."""
    statement = select(Task).where(Task.user_id == user_id)
    if completed is not None:
        statement = statement.where(Task.is_complete == completed)
    if priority:
        statement = statement.where(Task.priority == priority)
    if category:
        statement = statement.where(Task.category == category)
    return list(db.exec(statement).all())


def search_tasks(
    db: Session,
    user_id: int,
    *,
    q: Optional[str] = None,
    priority: Optional[str] = None,
    is_complete: Optional[bool] = None,
    tag: Optional[str] = None,
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> List[Task]:
    """Advanced search/filter/sort for Phase V."""
    statement = select(Task).where(Task.user_id == user_id)

    if q:
        statement = statement.where(col(Task.description).ilike(f"%{q}%"))
    if priority:
        statement = statement.where(Task.priority == priority)
    if is_complete is not None:
        statement = statement.where(Task.is_complete == is_complete)
    if tag:
        statement = statement.where(col(Task.tags).ilike(f"%{tag}%"))
    if due_before:
        statement = statement.where(Task.due_date <= due_before)
    if due_after:
        statement = statement.where(Task.due_date >= due_after)

    allowed_sort = {"created_at", "updated_at", "due_date", "priority"}
    sort_field = sort_by if sort_by in allowed_sort else "created_at"
    column = getattr(Task, sort_field)
    statement = statement.order_by(column.desc() if sort_order == "desc" else column.asc())

    return list(db.exec(statement).all())


def get_task_by_id(db: Session, task_id: int, user_id: int) -> Task:
    """Get a specific task by ID with user isolation."""
    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def get_overdue_tasks(db: Session, user_id: int) -> List[Task]:
    """Return incomplete tasks past their due date."""
    now = datetime.utcnow()
    statement = (
        select(Task)
        .where(Task.user_id == user_id, Task.is_complete == False, Task.due_date < now)  # noqa: E712
        .order_by(Task.due_date.asc())
    )
    return list(db.exec(statement).all())


def get_due_reminders(db: Session) -> List[Task]:
    """Return tasks whose reminder_at is in the past and are not yet complete."""
    now = datetime.utcnow()
    statement = (
        select(Task)
        .where(Task.is_complete == False, Task.reminder_at <= now)  # noqa: E712
    )
    return list(db.exec(statement).all())


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def create_task(
    db: Session,
    user_id: int,
    description: str,
    *,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[datetime] = None,
    reminder_at: Optional[datetime] = None,
    recurring_pattern: Optional[str] = None,
) -> Task:
    """Create a new task with Phase V advanced fields."""
    task = Task(
        description=description,
        user_id=user_id,
        priority=priority or "medium",
        tags=json.dumps(tags) if tags else None,
        due_date=due_date,
        reminder_at=reminder_at,
        recurring_pattern=recurring_pattern,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    logger.info("Task %s created for user %s", task.id, user_id)
    return task


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_task(
    db: Session,
    task_id: int,
    user_id: int,
    description: Optional[str] = None,
    is_complete: Optional[bool] = None,
    priority: Optional[str] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[datetime] = None,
    reminder_at: Optional[datetime] = None,
    recurring_pattern: Optional[str] = None,
) -> Task:
    """Partial update supporting all Phase V fields."""
    task = get_task_by_id(db, task_id, user_id)

    if description is not None:
        task.description = description
    if is_complete is not None:
        task.is_complete = is_complete
    if priority is not None:
        task.priority = priority
    if tags is not None:
        task.tags = json.dumps(tags)
    if due_date is not None:
        task.due_date = due_date
    if reminder_at is not None:
        task.reminder_at = reminder_at
    if recurring_pattern is not None:
        task.recurring_pattern = recurring_pattern

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    logger.info("Task %s updated for user %s", task.id, user_id)
    return task


def toggle_task(db: Session, task_id: int, user_id: int) -> Task:
    """Toggle a task's completion status."""
    task = get_task_by_id(db, task_id, user_id)
    task.is_complete = not task.is_complete
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_task(db: Session, task_id: int, user_id: int) -> None:
    """Delete a task with user isolation."""
    task = get_task_by_id(db, task_id, user_id)
    db.delete(task)
    db.commit()
    logger.info("Task %s deleted for user %s", task_id, user_id)


# ---------------------------------------------------------------------------
# Helpers (used by chat agent)
# ---------------------------------------------------------------------------

def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Get task by ID without user isolation (internal use only)."""
    return db.exec(select(Task).where(Task.id == task_id)).first()
