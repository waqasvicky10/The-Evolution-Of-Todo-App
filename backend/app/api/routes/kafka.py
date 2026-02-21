"""
Kafka API — Phase V.

Exposes the KafkaAgent and consumer services over REST endpoints.
All topic/cluster operations follow the P+Q+P pattern.
Consumer endpoints provide access to audit logs, sync feeds, and stats.
"""

from fastapi import APIRouter, Query
from typing import Any, Dict, List, Optional

from ...agents.kafka_agent import KafkaAgent
from ...services.consumers import (
    RecurringTaskConsumer,
    AuditLogConsumer,
    RealTimeSyncConsumer,
)

router = APIRouter(prefix="/api/kafka", tags=["kafka"])

# Singleton instances
_kafka_agent = KafkaAgent(dry_run=True)
_recurring_consumer = RecurringTaskConsumer()
_audit_consumer = AuditLogConsumer()
_realtime_consumer = RealTimeSyncConsumer()


# ------------------------------------------------------------------
# KafkaAgent status & setup
# ------------------------------------------------------------------

@router.get("/status")
def kafka_status() -> Dict[str, Any]:
    """Return current Kafka agent state and consumer stats."""
    return {
        "agent": _kafka_agent.get_status(),
        "consumers": {
            "recurring": _recurring_consumer.get_stats(),
            "audit": _audit_consumer.get_stats(),
            "realtime": _realtime_consumer.get_stats(),
        },
    }


@router.post("/setup")
def kafka_full_setup() -> Dict[str, Any]:
    """P+Q+P: Run the complete Kafka setup pipeline (topics, health, Dapr)."""
    return _kafka_agent.full_setup()


# ------------------------------------------------------------------
# Topic management
# ------------------------------------------------------------------

@router.post("/topics/create")
def create_topics() -> Dict[str, Any]:
    """P+Q+P: Create all Phase V Kafka topics."""
    step = _kafka_agent.create_topics()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.get("/topics")
def list_topics() -> Dict[str, Any]:
    """P+Q+P: List all topics on the broker."""
    step = _kafka_agent.list_topics()
    return {
        "topics": list(_kafka_agent.state.topics.keys()),
        "pqp": {"problem": step.problem, "question": step.question, "commands": step.pattern, "success": step.success},
    }


@router.get("/topics/{topic_name}")
def describe_topic(topic_name: str) -> Dict[str, Any]:
    """P+Q+P: Describe a specific topic."""
    step = _kafka_agent.describe_topic(topic_name)
    config = _kafka_agent.state.topics.get(topic_name, {})
    return {
        "topic": topic_name,
        "config": config,
        "pqp": {"problem": step.problem, "question": step.question, "commands": step.pattern, "success": step.success},
    }


# ------------------------------------------------------------------
# Cluster health
# ------------------------------------------------------------------

@router.get("/health")
def cluster_health() -> Dict[str, Any]:
    """P+Q+P: Check Redpanda cluster health."""
    step = _kafka_agent.check_cluster_health()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.get("/dapr-status")
def dapr_pubsub_status() -> Dict[str, Any]:
    """P+Q+P: Verify Dapr pubsub connectivity."""
    step = _kafka_agent.check_dapr_pubsub()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


# ------------------------------------------------------------------
# Consumer management
# ------------------------------------------------------------------

@router.get("/consumers")
def consumer_status() -> Dict[str, Any]:
    """P+Q+P: Check consumer group status."""
    step = _kafka_agent.get_consumer_status()
    return {
        "consumers": {
            "recurring": _recurring_consumer.get_stats(),
            "audit": _audit_consumer.get_stats(),
            "realtime": _realtime_consumer.get_stats(),
        },
        "pqp": {"problem": step.problem, "question": step.question, "commands": step.pattern, "success": step.success},
    }


@router.post("/consumers/reset")
def reset_consumer_offset(
    group: str = Query(...),
    topic: str = Query(...),
    offset: str = Query(default="earliest"),
) -> Dict[str, Any]:
    """P+Q+P: Reset a consumer group's offset."""
    step = _kafka_agent.reset_consumer_offset(group, topic, offset)
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


# ------------------------------------------------------------------
# Audit log
# ------------------------------------------------------------------

@router.get("/audit-log")
def get_audit_log(
    user_id: Optional[int] = Query(default=None),
    task_id: Optional[int] = Query(default=None),
    event_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
) -> List[Dict[str, Any]]:
    """Query the in-memory audit log with optional filters."""
    return _audit_consumer.query(user_id=user_id, task_id=task_id, event_type=event_type, limit=limit)


# ------------------------------------------------------------------
# Real-time sync feed
# ------------------------------------------------------------------

@router.get("/sync/{user_id}")
def get_sync_feed(
    user_id: int,
    since: Optional[str] = Query(default=None, description="ISO timestamp to get changes since"),
) -> Dict[str, Any]:
    """Get pending task changes for a user's real-time sync."""
    changes = _realtime_consumer.get_changes(user_id, since=since)
    return {
        "user_id": user_id,
        "changes": changes,
        "count": len(changes),
    }


@router.delete("/sync/{user_id}")
def clear_sync_feed(user_id: int) -> Dict[str, Any]:
    """Clear a user's sync feed after the frontend has consumed it."""
    cleared = _realtime_consumer.clear_feed(user_id)
    return {"user_id": user_id, "cleared": cleared}


# ------------------------------------------------------------------
# P+Q+P audit trail
# ------------------------------------------------------------------

@router.get("/pqp-trail")
def pqp_audit_trail() -> List[Dict[str, Any]]:
    """Return the full P+Q+P audit trail for all KafkaAgent operations."""
    return _kafka_agent.get_audit_trail()


# ------------------------------------------------------------------
# Expose consumer instances for main.py event handlers
# ------------------------------------------------------------------

def get_recurring_consumer() -> RecurringTaskConsumer:
    return _recurring_consumer

def get_audit_consumer() -> AuditLogConsumer:
    return _audit_consumer

def get_realtime_consumer() -> RealTimeSyncConsumer:
    return _realtime_consumer
