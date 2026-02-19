"""
Reminder service — Phase V.

Triggered by Dapr cron binding to check for due reminders
and publish reminder events to the pubsub topic.
"""

import logging
from app.database import get_session
from app.services.task_service import get_due_reminders
from app.services.event_service import emit_reminder

logger = logging.getLogger(__name__)


async def process_due_reminders() -> int:
    """
    Check for tasks with due reminders and publish events.
    Returns the count of reminders processed.
    """
    count = 0
    for session in get_session():
        tasks = get_due_reminders(session)
        for task in tasks:
            try:
                await emit_reminder(
                    task_id=task.id,
                    user_id=task.user_id,
                    description=task.description,
                )
                task.reminder_at = None
                session.commit()
                count += 1
            except Exception as exc:
                logger.error("Failed to process reminder for task %s: %s", task.id, exc)
    logger.info("Processed %d due reminders", count)
    return count
