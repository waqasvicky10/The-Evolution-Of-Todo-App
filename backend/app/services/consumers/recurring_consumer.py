"""
RecurringTaskConsumer — Phase V.

Consumes events from the 'recurring-tasks' topic.
When a recurring task is completed, this consumer auto-reschedules
it by creating a new task with the next due date.

Integrates with Dapr pubsub (events arrive at /events/recurring-tasks endpoint).
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_PATTERN_DELTAS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "monthly": timedelta(days=30),
}


class RecurringTaskConsumer:
    """
    Processes 'task.needs_reschedule' events.

    When a recurring task is completed:
    1. Reads the recurring_pattern (daily/weekly/monthly)
    2. Calculates the next due_date
    3. Creates a new task with the shifted due_date
    4. Publishes a task.created event for the new task
    """

    def __init__(self):
        self.processed_count = 0
        self.errors: list[Dict[str, Any]] = []
        logger.info("RecurringTaskConsumer initialised")

    @staticmethod
    def calculate_next_due(current_due: Optional[datetime], pattern: str) -> datetime:
        """Calculate the next due date based on the recurring pattern."""
        base = current_due or datetime.utcnow()
        delta = _PATTERN_DELTAS.get(pattern)
        if not delta:
            logger.warning("Unknown recurring pattern: %s, defaulting to weekly", pattern)
            delta = timedelta(weeks=1)

        next_due = base + delta
        if next_due <= datetime.utcnow():
            next_due = datetime.utcnow() + delta
        return next_due

    async def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single recurring-task event.

        Args:
            event_data: Dapr CloudEvent data with task_id, user_id, recurring_pattern

        Returns:
            Result dict with the new task info or error
        """
        event = event_data.get("data", event_data)
        task_id = event.get("task_id")
        user_id = event.get("user_id")
        pattern = event.get("recurring_pattern")

        if not all([task_id, user_id, pattern]):
            error = {"error": "Missing required fields", "event": event}
            self.errors.append(error)
            logger.error("[RecurringConsumer] %s", error)
            return error

        logger.info(
            "[RecurringConsumer] Rescheduling task %s for user %s (pattern=%s)",
            task_id, user_id, pattern,
        )

        try:
            from app.database import get_session
            from app.services.task_service import get_task, create_task

            next_due = self.calculate_next_due(None, pattern)

            for session in get_session():
                original = get_task(session, task_id)
                if not original:
                    return {"error": f"Task {task_id} not found", "task_id": task_id}

                new_task = create_task(
                    session,
                    user_id=user_id,
                    description=original.description,
                    priority=original.priority,
                    tags=original.tags_list if original.tags else None,
                    due_date=next_due,
                    recurring_pattern=pattern,
                )

                self.processed_count += 1
                result = {
                    "action": "rescheduled",
                    "original_task_id": task_id,
                    "new_task_id": new_task.id,
                    "next_due_date": next_due.isoformat(),
                    "pattern": pattern,
                }
                logger.info("[RecurringConsumer] Created task %s (next due: %s)", new_task.id, next_due)
                return result

        except Exception as exc:
            error = {"error": str(exc), "task_id": task_id}
            self.errors.append(error)
            logger.error("[RecurringConsumer] Failed: %s", exc)
            return error

    def get_stats(self) -> Dict[str, Any]:
        return {
            "consumer": "RecurringTaskConsumer",
            "processed": self.processed_count,
            "errors": len(self.errors),
        }
