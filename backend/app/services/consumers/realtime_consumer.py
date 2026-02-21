"""
RealTimeSyncConsumer — Phase V.

Consumes events from 'task-updates' and 'task-events' topics.
Maintains a per-user change feed that frontends can poll
for real-time synchronisation without WebSockets.

The frontend polls GET /api/kafka/sync/{user_id} to fetch
pending changes since their last poll timestamp.
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RealTimeSyncConsumer:
    """
    Aggregates task events into per-user change feeds.

    Each user has a bounded queue of recent changes.
    The frontend polls to retrieve changes since a given timestamp,
    enabling optimistic UI updates and conflict detection.
    """

    MAX_PER_USER = 200

    def __init__(self):
        self._feeds: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        self.processed_count = 0
        self.errors: list[Dict[str, Any]] = []
        logger.info("RealTimeSyncConsumer initialised")

    async def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task event and add it to the user's change feed.

        Args:
            event_data: Dapr CloudEvent data

        Returns:
            Acknowledgement dict
        """
        event = event_data.get("data", event_data)
        user_id = event.get("user_id")

        if user_id is None:
            error = {"error": "Missing user_id in event", "event": event}
            self.errors.append(error)
            return error

        change = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event.get("event", "unknown"),
            "task_id": event.get("task_id"),
            "changes": event.get("changes", {}),
            "description": event.get("description"),
        }

        feed = self._feeds[user_id]
        feed.append(change)
        if len(feed) > self.MAX_PER_USER:
            self._feeds[user_id] = feed[-self.MAX_PER_USER:]

        self.processed_count += 1
        logger.debug(
            "[SyncConsumer] User %s: %s (task %s)",
            user_id, change["event_type"], change["task_id"],
        )

        return {"status": "queued", "user_id": user_id, "feed_size": len(self._feeds[user_id])}

    def get_changes(self, user_id: int, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get pending changes for a user since a given ISO timestamp.

        Args:
            user_id: The user to get changes for
            since: ISO timestamp; if None, returns all buffered changes

        Returns:
            List of change events
        """
        feed = self._feeds.get(user_id, [])
        if since is None:
            return list(feed)
        return [c for c in feed if c["timestamp"] > since]

    def clear_feed(self, user_id: int) -> int:
        """Clear a user's change feed. Returns number of cleared entries."""
        count = len(self._feeds.get(user_id, []))
        self._feeds[user_id] = []
        return count

    def get_stats(self) -> Dict[str, Any]:
        return {
            "consumer": "RealTimeSyncConsumer",
            "active_users": len(self._feeds),
            "total_buffered": sum(len(f) for f in self._feeds.values()),
            "processed": self.processed_count,
            "errors": len(self.errors),
        }
