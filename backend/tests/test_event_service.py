"""
Phase V — Event service tests (mock Dapr/Redpanda).

Verifies that event publishing works correctly when Dapr sidecar
is unavailable (mock mode — logged only).
"""

import pytest
import logging
from unittest.mock import patch, AsyncMock

from app.services.event_service import (
    publish_event,
    emit_task_created,
    emit_task_deleted,
    emit_task_completed,
    emit_reminder,
    _check_dapr,
    TOPIC_TASK_EVENTS,
    TOPIC_REMINDERS,
)


@pytest.fixture(autouse=True)
def reset_dapr_cache():
    """Reset the cached Dapr availability flag between tests."""
    import app.services.event_service as svc
    svc._dapr_available = None
    yield
    svc._dapr_available = None


@pytest.mark.asyncio
async def test_publish_event_logs_when_no_dapr(caplog):
    """Without Dapr sidecar, events are logged (not HTTP-published)."""
    with caplog.at_level(logging.INFO):
        await publish_event("test-topic", {"key": "value"})
    assert "[Event:test-topic]" in caplog.text


@pytest.mark.asyncio
async def test_emit_task_created():
    with patch("app.services.event_service.publish_event", new_callable=AsyncMock) as mock:
        await emit_task_created(task_id=1, user_id=2, description="Test")
        mock.assert_called_once()
        args = mock.call_args
        assert args[0][0] == TOPIC_TASK_EVENTS
        assert args[0][1]["event"] == "task.created"


@pytest.mark.asyncio
async def test_emit_task_deleted():
    with patch("app.services.event_service.publish_event", new_callable=AsyncMock) as mock:
        await emit_task_deleted(task_id=5, user_id=1)
        mock.assert_called_once()
        assert mock.call_args[0][1]["event"] == "task.deleted"


@pytest.mark.asyncio
async def test_emit_task_completed():
    with patch("app.services.event_service.publish_event", new_callable=AsyncMock) as mock:
        await emit_task_completed(task_id=3, user_id=1)
        mock.assert_called_once()
        assert mock.call_args[0][1]["event"] == "task.completed"


@pytest.mark.asyncio
async def test_emit_reminder():
    with patch("app.services.event_service.publish_event", new_callable=AsyncMock) as mock:
        await emit_reminder(task_id=7, user_id=1, description="Don't forget")
        mock.assert_called_once()
        assert mock.call_args[0][0] == TOPIC_REMINDERS
