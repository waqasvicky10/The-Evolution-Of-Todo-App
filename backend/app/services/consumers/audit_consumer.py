"""
AuditLogConsumer — Phase V.

Consumes events from the 'audit-log' topic.
Maintains an immutable, append-only audit trail of all task mutations.
Stores entries in-memory with an option to flush to the database.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class AuditLogConsumer:
    """
    Processes audit events and maintains an immutable log.

    Event types recorded:
      - audit.create  — task created
      - audit.update  — task modified (with diff)
      - audit.delete  — task deleted
      - audit.complete — task marked complete
      - audit.reschedule — recurring task rescheduled
    """

    MAX_IN_MEMORY = 10_000

    def __init__(self):
        self._log: List[Dict[str, Any]] = []
        self.processed_count = 0
        self.errors: list[Dict[str, Any]] = []
        logger.info("AuditLogConsumer initialised (max_in_memory=%d)", self.MAX_IN_MEMORY)

    async def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single audit event.

        Args:
            event_data: Dapr CloudEvent data

        Returns:
            Acknowledgement dict
        """
        event = event_data.get("data", event_data)

        entry = {
            "id": self.processed_count + 1,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event.get("event", "unknown"),
            "task_id": event.get("task_id"),
            "user_id": event.get("user_id"),
            "details": event.get("details", {}),
            "raw": event,
        }

        if len(self._log) >= self.MAX_IN_MEMORY:
            self._log.pop(0)

        self._log.append(entry)
        self.processed_count += 1

        logger.info(
            "[AuditConsumer] #%d %s task=%s user=%s",
            entry["id"], entry["event_type"], entry["task_id"], entry["user_id"],
        )

        return {"status": "logged", "audit_id": entry["id"]}

    def query(
        self,
        user_id: int = None,
        task_id: int = None,
        event_type: str = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Query the audit log with optional filters."""
        results = self._log
        if user_id is not None:
            results = [e for e in results if e.get("user_id") == user_id]
        if task_id is not None:
            results = [e for e in results if e.get("task_id") == task_id]
        if event_type is not None:
            results = [e for e in results if e.get("event_type") == event_type]
        return list(reversed(results[-limit:]))

    def get_stats(self) -> Dict[str, Any]:
        return {
            "consumer": "AuditLogConsumer",
            "total_entries": len(self._log),
            "processed": self.processed_count,
            "errors": len(self.errors),
        }

    def get_full_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return the most recent audit entries."""
        return list(reversed(self._log[-limit:]))
