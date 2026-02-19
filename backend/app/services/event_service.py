"""
Event publisher service — Phase V.

Publishes task lifecycle events to Dapr pubsub (backed by Redpanda/Kafka).
Falls back to logging when Dapr sidecar is unavailable (Vercel, local dev).
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = "task-pubsub"
TOPIC_TASK_EVENTS = "task-events"
TOPIC_REMINDERS = "reminders"
TOPIC_TASK_UPDATES = "task-updates"


def _is_dapr_available() -> bool:
    """Check if the Dapr sidecar is reachable (fast fail for Vercel/local)."""
    if os.getenv("VERCEL") == "1":
        return False
    try:
        resp = httpx.get(f"{DAPR_BASE_URL}/v1.0/healthz", timeout=0.5)
        return resp.status_code == 204 or resp.status_code == 200
    except Exception:
        return False


_dapr_available: Optional[bool] = None


def _check_dapr() -> bool:
    global _dapr_available
    if _dapr_available is None:
        _dapr_available = _is_dapr_available()
        if _dapr_available:
            logger.info("Dapr sidecar detected — events will be published.")
        else:
            logger.info("Dapr sidecar not found — events will be logged only.")
    return _dapr_available


async def publish_event(topic: str, data: Dict[str, Any]) -> None:
    """Publish an event to a Dapr pubsub topic (async, fire-and-forget)."""
    payload = {**data, "published_at": datetime.utcnow().isoformat()}

    if not _check_dapr():
        logger.info("[Event:%s] %s", topic, json.dumps(payload, default=str))
        return

    url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=2.0,
            )
            resp.raise_for_status()
            logger.info("[Event:%s] Published successfully", topic)
    except Exception as exc:
        logger.warning("[Event:%s] Publish failed: %s", topic, exc)


# ---- Convenience wrappers ----

async def emit_task_created(task_id: int, user_id: int, description: str) -> None:
    await publish_event(TOPIC_TASK_EVENTS, {
        "event": "task.created",
        "task_id": task_id,
        "user_id": user_id,
        "description": description,
    })


async def emit_task_updated(task_id: int, user_id: int, changes: Dict[str, Any]) -> None:
    await publish_event(TOPIC_TASK_UPDATES, {
        "event": "task.updated",
        "task_id": task_id,
        "user_id": user_id,
        "changes": changes,
    })


async def emit_task_deleted(task_id: int, user_id: int) -> None:
    await publish_event(TOPIC_TASK_EVENTS, {
        "event": "task.deleted",
        "task_id": task_id,
        "user_id": user_id,
    })


async def emit_task_completed(task_id: int, user_id: int) -> None:
    await publish_event(TOPIC_TASK_EVENTS, {
        "event": "task.completed",
        "task_id": task_id,
        "user_id": user_id,
    })


async def emit_reminder(task_id: int, user_id: int, description: str) -> None:
    await publish_event(TOPIC_REMINDERS, {
        "event": "task.reminder",
        "task_id": task_id,
        "user_id": user_id,
        "description": description,
    })
