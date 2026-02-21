"""
AdvancedFeatureAgent — Phase V.

AI-assisted agent for managing all Phase V advanced todo features:
  - Recurring tasks (daily/weekly/monthly auto-reschedule)
  - Due dates & reminders (Dapr cron binding)
  - Priorities (low/medium/high/urgent)
  - Tags (user-defined hashtags)
  - Search/filter/sort (keyword, priority, tag, due date range)

Every operation follows the P+Q+P pattern.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


PRIORITY_LEVELS = ["low", "medium", "high", "urgent"]
RECURRING_PATTERNS = ["daily", "weekly", "monthly"]
SORT_FIELDS = ["created_at", "updated_at", "due_date", "priority"]


@dataclass
class PQPStep:
    problem: str
    question: str
    pattern: List[str]
    result: Optional[str] = None
    success: bool = False


@dataclass
class AdvancedFeatureState:
    """Tracks feature usage statistics."""
    tasks_created_with_priority: int = 0
    tasks_created_with_tags: int = 0
    tasks_created_with_due_date: int = 0
    tasks_created_recurring: int = 0
    reminders_set: int = 0
    searches_performed: int = 0
    recurring_rescheduled: int = 0
    steps: List[PQPStep] = field(default_factory=list)


class AdvancedFeatureAgent:
    """
    Orchestrates Phase V advanced features with P+Q+P documentation.

    Features:
      1. Recurring Tasks — auto-reschedule on completion via Kafka consumer
      2. Due Dates & Reminders — Dapr cron binding checks every 5m
      3. Priorities — low/medium/high/urgent with sorting
      4. Tags — user-defined hashtags for categorisation
      5. Search/Filter/Sort — keyword, priority, tag, due date range
    """

    def __init__(self):
        self.state = AdvancedFeatureState()
        logger.info("AdvancedFeatureAgent initialised")

    def _pqp(self, problem: str, question: str, pattern: List[str]) -> PQPStep:
        step = PQPStep(problem=problem, question=question, pattern=pattern)
        step.result = "\n".join(pattern)
        step.success = True
        self.state.steps.append(step)
        return step

    # ------------------------------------------------------------------
    # 1. RECURRING TASKS (P+Q+P)
    # ------------------------------------------------------------------

    def explain_recurring(self) -> PQPStep:
        """P+Q+P: How recurring tasks work end-to-end."""
        return self._pqp(
            problem="User wants a task to repeat automatically after completion.",
            question="How does the recurring task system work?",
            pattern=[
                "1. User creates task with recurring_pattern='weekly'",
                "2. POST /api/tasks → create_task(recurring_pattern='weekly')",
                "3. User completes the task → PATCH /api/tasks/{id}/toggle",
                "4. toggle_task_endpoint calls emit_task_completed(recurring_pattern='weekly')",
                "5. event_service publishes to 'recurring-tasks' Kafka topic",
                "6. Dapr routes event to /events/recurring-tasks endpoint",
                "7. RecurringTaskConsumer.process_event() fires:",
                "   - Calculates next due_date (current + 7 days for weekly)",
                "   - Creates new task with same description, priority, tags",
                "   - New task has updated due_date, same recurring_pattern",
                "8. Cycle repeats on next completion",
            ],
        )

    def calculate_next_due(self, current_due: Optional[datetime], pattern: str) -> Dict[str, Any]:
        """P+Q+P: Calculate the next due date for a recurring task."""
        deltas = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1), "monthly": timedelta(days=30)}
        base = current_due or datetime.utcnow()
        delta = deltas.get(pattern, timedelta(weeks=1))
        next_due = base + delta
        if next_due <= datetime.utcnow():
            next_due = datetime.utcnow() + delta

        self._pqp(
            problem=f"Recurring task with pattern '{pattern}' needs next due date.",
            question=f"What is the next due date after {base.isoformat()}?",
            pattern=[f"Base: {base.isoformat()}", f"Pattern: {pattern}", f"Delta: {delta}", f"Next due: {next_due.isoformat()}"],
        )
        return {"pattern": pattern, "base": base.isoformat(), "next_due": next_due.isoformat()}

    # ------------------------------------------------------------------
    # 2. DUE DATES & REMINDERS (P+Q+P)
    # ------------------------------------------------------------------

    def explain_reminders(self) -> PQPStep:
        """P+Q+P: How the reminder system works."""
        return self._pqp(
            problem="User wants to be reminded about a task before its due date.",
            question="How does the Dapr cron reminder system work?",
            pattern=[
                "1. User creates task with reminder_at='2026-03-01T09:00:00'",
                "2. Dapr cron binding (reminder-cron) fires every 5 minutes",
                "3. POST /reminder-cron → process_due_reminders()",
                "4. Queries: SELECT * FROM tasks WHERE reminder_at <= NOW() AND is_complete = FALSE",
                "5. For each due task: emit_reminder(task_id, user_id, description)",
                "6. Publishes to 'reminders' Kafka topic",
                "7. Sets reminder_at = NULL to prevent duplicate reminders",
                "8. AuditLogConsumer records the reminder event",
            ],
        )

    # ------------------------------------------------------------------
    # 3. PRIORITIES (P+Q+P)
    # ------------------------------------------------------------------

    def explain_priorities(self) -> PQPStep:
        """P+Q+P: How priority levels work."""
        return self._pqp(
            problem="User needs to organise tasks by importance/urgency.",
            question="How do priority levels affect task management?",
            pattern=[
                "Levels: low → medium → high → urgent",
                "Storage: Task.priority column (indexed for fast queries)",
                "Create: POST /api/tasks {priority: 'high'}",
                "Update: PUT /api/tasks/{id} {priority: 'urgent'}",
                "Filter: GET /api/tasks/search?priority=high",
                "Sort: GET /api/tasks/search?sort_by=priority&sort_order=desc",
                "Chat: 'Set task 5 priority to high' → mock_provider routes to update_todo",
                "Display: Frontend shows coloured badges (red=high, purple=urgent, yellow=medium, green=low)",
            ],
        )

    # ------------------------------------------------------------------
    # 4. TAGS (P+Q+P)
    # ------------------------------------------------------------------

    def explain_tags(self) -> PQPStep:
        """P+Q+P: How the tagging system works."""
        return self._pqp(
            problem="User wants to categorise tasks with custom labels.",
            question="How do tags work across the stack?",
            pattern=[
                "Storage: Task.tags column as JSON string ('[\"work\",\"urgent\"]')",
                "Serialise: json.dumps(tags) on save, json.loads() on read",
                "Property: task.tags_list getter/setter for clean Python list access",
                "Create: POST /api/tasks {tags: ['work', 'meeting']}",
                "Filter: GET /api/tasks/search?tag=work (ILIKE substring match)",
                "Chat: 'Add task deploy backend #devops #urgent' → extracts #hashtags",
                "Display: Frontend shows teal pills (#work, #meeting)",
                "NLP: task_parser.extract_tags() finds #hashtags in natural language",
            ],
        )

    # ------------------------------------------------------------------
    # 5. SEARCH / FILTER / SORT (P+Q+P)
    # ------------------------------------------------------------------

    def explain_search(self) -> PQPStep:
        """P+Q+P: How advanced search works."""
        return self._pqp(
            problem="User needs to find specific tasks among many.",
            question="What search, filter, and sort capabilities are available?",
            pattern=[
                "Endpoint: GET /api/tasks/search",
                "Keyword: ?q=groceries → ILIKE '%groceries%' on description",
                "Priority: ?priority=high → exact match",
                "Status: ?is_complete=false → incomplete only",
                "Tag: ?tag=work → ILIKE '%work%' on tags JSON",
                "Due before: ?due_before=2026-03-01 → due_date <= date",
                "Due after: ?due_after=2026-02-01 → due_date >= date",
                "Sort: ?sort_by=due_date&sort_order=asc → ordered by deadline",
                "Overdue: GET /api/tasks/overdue → past due_date + incomplete",
                "Chat: 'Search for urgent work tasks' → search_todos tool",
                "Chat: 'Show overdue tasks' → get_overdue_todos tool",
            ],
        )

    # ------------------------------------------------------------------
    # Feature matrix
    # ------------------------------------------------------------------

    def get_feature_matrix(self) -> Dict[str, Any]:
        """Return the complete Phase V feature matrix."""
        return {
            "recurring_tasks": {
                "patterns": RECURRING_PATTERNS,
                "flow": "complete → Kafka → RecurringTaskConsumer → new task",
                "model_field": "Task.recurring_pattern",
            },
            "due_dates_reminders": {
                "model_fields": ["Task.due_date", "Task.reminder_at"],
                "cron": "Dapr binding @every 5m → POST /reminder-cron",
                "overdue_endpoint": "GET /api/tasks/overdue",
            },
            "priorities": {
                "levels": PRIORITY_LEVELS,
                "model_field": "Task.priority (indexed)",
                "default": "medium",
            },
            "tags": {
                "storage": "JSON string in Task.tags",
                "access": "task.tags_list property",
                "search": "ILIKE substring match",
            },
            "search_filter_sort": {
                "endpoint": "GET /api/tasks/search",
                "filters": ["q", "priority", "is_complete", "tag", "due_before", "due_after"],
                "sort_fields": SORT_FIELDS,
                "sort_orders": ["asc", "desc"],
            },
        }

    # ------------------------------------------------------------------
    # Chat command reference
    # ------------------------------------------------------------------

    def get_chat_commands(self) -> List[Dict[str, str]]:
        """Return all Phase V chat commands the agent understands."""
        return [
            {"command": "Add urgent task deploy backend by Friday #devops", "feature": "priority + tags + due date"},
            {"command": "Set task 5 priority to high", "feature": "priority update"},
            {"command": "Make task 3 repeat weekly", "feature": "recurring"},
            {"command": "Search for urgent work tasks", "feature": "search + priority filter"},
            {"command": "Show overdue tasks", "feature": "overdue detection"},
            {"command": "Find tasks tagged #shopping", "feature": "tag search"},
            {"command": "Show tasks due this week", "feature": "due date range"},
            {"command": "List high priority tasks", "feature": "priority filter"},
            {"command": "فوری ٹاسک شامل کریں", "feature": "Urdu priority"},
            {"command": "مدت ختم شدہ ٹاسک دکھائیں", "feature": "Urdu overdue"},
        ]

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        return {
            "features": list(self.get_feature_matrix().keys()),
            "chat_commands": len(self.get_chat_commands()),
            "priority_levels": PRIORITY_LEVELS,
            "recurring_patterns": RECURRING_PATTERNS,
            "stats": {
                "priority_tasks": self.state.tasks_created_with_priority,
                "tagged_tasks": self.state.tasks_created_with_tags,
                "due_date_tasks": self.state.tasks_created_with_due_date,
                "recurring_tasks": self.state.tasks_created_recurring,
                "reminders_set": self.state.reminders_set,
                "searches": self.state.searches_performed,
                "rescheduled": self.state.recurring_rescheduled,
            },
            "total_pqp_steps": len(self.state.steps),
        }

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return [
            {"problem": s.problem, "question": s.question, "pattern": s.pattern, "success": s.success}
            for s in self.state.steps
        ]
