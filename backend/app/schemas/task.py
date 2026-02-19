"""
Task request and response schemas — Phase V.

Pydantic models for task CRUD operations with validation.
Supports advanced fields: priority, tags, due_date, recurring, reminders.
"""

from datetime import datetime
from pydantic import BaseModel, constr, field_validator, field_serializer
from typing import List, Optional
from enum import Enum


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class RecurringPattern(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class TaskCreate(BaseModel):
    """Task creation request — Phase V."""

    description: constr(min_length=1, max_length=500)
    priority: Optional[PriorityEnum] = PriorityEnum.medium
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    recurring_pattern: Optional[RecurringPattern] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Task description cannot be empty")
        return trimmed


class TaskUpdate(BaseModel):
    """Task update request — Phase V (all fields optional for partial update)."""

    description: Optional[constr(min_length=1, max_length=500)] = None
    is_complete: Optional[bool] = None
    priority: Optional[PriorityEnum] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    recurring_pattern: Optional[RecurringPattern] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Task description cannot be empty")
        return trimmed


class TaskResponse(BaseModel):
    """Task response — Phase V with all advanced fields."""

    id: int
    description: str
    is_complete: bool
    user_id: int
    priority: Optional[str] = "medium"
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    recurring_pattern: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    @classmethod
    def serialize_datetime(cls, v: datetime) -> str:
        return v.isoformat()

    @field_serializer("due_date", "reminder_at")
    @classmethod
    def serialize_optional_datetime(cls, v: Optional[datetime]) -> Optional[str]:
        return v.isoformat() if v else None

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Task list response with total count."""

    tasks: List[TaskResponse]
    total: int


class TaskSearchParams(BaseModel):
    """Query parameters for task search/filter/sort."""

    q: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    is_complete: Optional[bool] = None
    tag: Optional[str] = None
    due_before: Optional[datetime] = None
    due_after: Optional[datetime] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
