"""
Phase V — Dapr integration endpoint tests.

Tests the Dapr subscription discovery endpoint, cron binding handler,
and event receiver endpoints.
"""


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["phase"] == "V"


def test_root_shows_phase_v(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["version"] == "5.0.0"
    assert "event-driven" in data["features"]


def test_dapr_subscribe_endpoint(client):
    """Dapr discovers subscriptions via GET /dapr/subscribe."""
    resp = client.get("/dapr/subscribe")
    assert resp.status_code == 200
    subs = resp.json()
    topics = [s["topic"] for s in subs]
    assert "task-events" in topics
    assert "reminders" in topics
    assert "task-updates" in topics


def test_cron_handler(client):
    """Dapr cron binding POSTs to /reminder-cron."""
    resp = client.post("/reminder-cron")
    assert resp.status_code == 200
    assert "processed" in resp.json()


def test_event_receiver_task_events(client):
    resp = client.post("/events/task-events", json={"data": {"event": "task.created", "task_id": 1}})
    assert resp.status_code == 200


def test_event_receiver_reminders(client):
    resp = client.post("/events/reminders", json={"data": {"task_id": 1}})
    assert resp.status_code == 200


def test_event_receiver_task_updates(client):
    resp = client.post("/events/task-updates", json={"data": {"event": "task.updated"}})
    assert resp.status_code == 200
