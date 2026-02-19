"""
Task database model — Phase V.

Defines the Task entity with SQLModel for database operations.
Supports advanced features: due dates, recurring tasks, reminders,
priorities, tags, and AI-enhanced fields.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import json

if TYPE_CHECKING:
    from app.models.user import User


class Task(SQLModel, table=True):
    """
    Task model representing todo items in the system.

    Each task belongs to exactly one user (user_id foreign key).
    Phase V adds due dates, recurring schedules, reminders,
    searchable tags, and priority levels.
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(max_length=500, min_length=1)
    is_complete: bool = Field(default=False)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Phase V — Advanced fields
    priority: Optional[str] = Field(default="medium", max_length=20, index=True)
    tags: Optional[str] = Field(default=None, max_length=500)
    due_date: Optional[datetime] = Field(default=None, index=True)
    reminder_at: Optional[datetime] = Field(default=None)
    recurring_pattern: Optional[str] = Field(default=None, max_length=50)

    # AI-enhanced fields (carried forward from Phase IV)
    category: Optional[str] = Field(default=None, max_length=50)
    estimated_duration: Optional[str] = Field(default=None, max_length=50)
    ai_tags: Optional[str] = Field(default=None, max_length=500)
    ai_suggestions: Optional[str] = Field(default=None, max_length=1000)

    # Relationship to user
    user: "User" = Relationship(back_populates="tasks")

    @property
    def tags_list(self) -> list[str]:
        """Deserialise the JSON tags string into a Python list."""
        if not self.tags:
            return []
        try:
            return json.loads(self.tags)
        except (json.JSONDecodeError, TypeError):
            return [t.strip() for t in self.tags.split(",") if t.strip()]

    @tags_list.setter
    def tags_list(self, value: list[str]) -> None:
        self.tags = json.dumps(value) if value else None

    @property
    def is_overdue(self) -> bool:
        return (
            self.due_date is not None
            and not self.is_complete
            and self.due_date < datetime.utcnow()
        )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, user_id={self.user_id}, priority={self.priority}, complete={self.is_complete})>"
