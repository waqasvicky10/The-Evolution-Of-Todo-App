"""
Task management API routes — Phase V.

Endpoints for task CRUD with advanced search/filter/sort, priority,
tags, due dates, recurring tasks, and reminders.
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlmodel import Session

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskListResponse,
    TaskResponse,
    PriorityEnum,
)
from app.services.task_service import (
    create_task,
    get_task_by_id,
    get_user_tasks,
    search_tasks,
    update_task,
    delete_task,
    toggle_task,
    get_overdue_tasks,
)
from app.services.event_service import (
    emit_task_created,
    emit_task_updated,
    emit_task_deleted,
    emit_task_completed,
)
from app.api.deps import get_db, get_current_user
from app.models.user import User


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _task_to_response(task) -> TaskResponse:
    """Convert a Task model to a TaskResponse, deserialising JSON tags."""
    data = {
        "id": task.id,
        "description": task.description,
        "is_complete": task.is_complete,
        "user_id": task.user_id,
        "priority": task.priority,
        "tags": task.tags_list,
        "due_date": task.due_date,
        "reminder_at": task.reminder_at,
        "recurring_pattern": task.recurring_pattern,
        "category": task.category,
        "created_at": task.created_at,
        "updated_at": task.updated_at,
    }
    return TaskResponse(**data)


@router.get("", response_model=TaskListResponse)
def list_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all tasks for the authenticated user.

    Returns only tasks that belong to the authenticated user (user isolation).

    Args:
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        List of tasks and total count

    Requires:
        Valid JWT token in Authorization header

    Raises:
        401: Not authenticated or invalid token

    Example:
        GET /api/tasks
        Headers: Authorization: Bearer <access_token>

        Response 200:
        {
            "tasks": [
                {
                    "id": 1,
                    "description": "Buy groceries",
                    "is_complete": false,
                    "user_id": 1,
                    "created_at": "2026-01-01T12:00:00Z",
                    "updated_at": "2026-01-01T12:00:00Z"
                }
            ],
            "total": 1
        }
    """
    tasks = get_user_tasks(db, user_id=current_user.id)
    return TaskListResponse(
        tasks=[_task_to_response(t) for t in tasks],
        total=len(tasks),
    )


@router.get("/search", response_model=TaskListResponse)
def search_tasks_endpoint(
    q: Optional[str] = Query(None, description="Full-text keyword search"),
    priority: Optional[PriorityEnum] = Query(None),
    is_complete: Optional[bool] = Query(None),
    tag: Optional[str] = Query(None, description="Filter by tag substring"),
    due_before: Optional[datetime] = Query(None),
    due_after: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="asc or desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase V: Search, filter, and sort tasks."""
    tasks = search_tasks(
        db,
        user_id=current_user.id,
        q=q,
        priority=priority.value if priority else None,
        is_complete=is_complete,
        tag=tag,
        due_before=due_before,
        due_after=due_after,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return TaskListResponse(
        tasks=[_task_to_response(t) for t in tasks],
        total=len(tasks),
    )


@router.get("/overdue", response_model=TaskListResponse)
def overdue_tasks_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase V: Get overdue tasks (past due_date, not complete)."""
    tasks = get_overdue_tasks(db, user_id=current_user.id)
    return TaskListResponse(
        tasks=[_task_to_response(t) for t in tasks],
        total=len(tasks),
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(
    request: TaskCreate,
    bg: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new task with Phase V advanced fields."""
    task = create_task(
        db,
        user_id=current_user.id,
        description=request.description,
        priority=request.priority.value if request.priority else "medium",
        tags=request.tags,
        due_date=request.due_date,
        reminder_at=request.reminder_at,
        recurring_pattern=request.recurring_pattern.value if request.recurring_pattern else None,
    )
    bg.add_task(emit_task_created, task.id, current_user.id, task.description)
    return _task_to_response(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_endpoint(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific task by ID."""
    task = get_task_by_id(db, task_id=task_id, user_id=current_user.id)
    return _task_to_response(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(
    task_id: int,
    request: TaskUpdate,
    bg: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Phase V: Partial update supporting all advanced fields."""
    task = update_task(
        db,
        task_id=task_id,
        user_id=current_user.id,
        description=request.description,
        is_complete=request.is_complete,
        priority=request.priority.value if request.priority else None,
        tags=request.tags,
        due_date=request.due_date,
        reminder_at=request.reminder_at,
        recurring_pattern=request.recurring_pattern.value if request.recurring_pattern else None,
    )
    if request.is_complete and task.is_complete and task.recurring_pattern:
        bg.add_task(emit_task_completed, task.id, current_user.id, task.recurring_pattern)
    else:
        bg.add_task(emit_task_updated, task.id, current_user.id, {"updated": True})
    return _task_to_response(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    task_id: int,
    bg: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a task permanently."""
    delete_task(db, task_id=task_id, user_id=current_user.id)
    bg.add_task(emit_task_deleted, task_id, current_user.id)


@router.patch("/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task_endpoint(
    task_id: int,
    bg: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggle a task's completion status."""
    task = toggle_task(db, task_id=task_id, user_id=current_user.id)
    if task.is_complete:
        bg.add_task(emit_task_completed, task.id, current_user.id, task.recurring_pattern)
    else:
        bg.add_task(emit_task_updated, task.id, current_user.id, {"is_complete": False})
    return _task_to_response(task)
