"""
Kafka consumer services — Phase V.

Each consumer processes events from a specific Redpanda topic
and performs the corresponding business logic.
"""

from .recurring_consumer import RecurringTaskConsumer
from .audit_consumer import AuditLogConsumer
from .realtime_consumer import RealTimeSyncConsumer

__all__ = [
    "RecurringTaskConsumer",
    "AuditLogConsumer",
    "RealTimeSyncConsumer",
]
