"""
Phase V — Advanced task feature tests.

Tests: create with priority/tags/due_date, search, filter, sort, overdue.
"""

import json
from datetime import datetime, timedelta


def test_create_task_with_advanced_fields(client, auth_headers):
    """Create a task with priority, tags, due_date."""
    due = (datetime.utcnow() + timedelta(days=7)).isoformat()
    resp = client.post(
        "/api/tasks",
        json={
            "description": "Advanced task",
            "priority": "high",
            "tags": ["work", "urgent"],
            "due_date": due,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["priority"] == "high"
    assert "work" in data["tags"]
    assert data["due_date"] is not None


def test_create_task_default_priority(client, auth_headers):
    resp = client.post(
        "/api/tasks",
        json={"description": "Simple task"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["priority"] == "medium"


def test_update_task_partial(client, auth_headers):
    resp = client.post(
        "/api/tasks",
        json={"description": "Old desc"},
        headers=auth_headers,
    )
    task_id = resp.json()["id"]

    resp = client.put(
        f"/api/tasks/{task_id}",
        json={"priority": "urgent", "tags": ["critical"]},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["priority"] == "urgent"
    assert "critical" in resp.json()["tags"]
    assert resp.json()["description"] == "Old desc"


def test_search_by_keyword(client, auth_headers):
    client.post("/api/tasks", json={"description": "Buy groceries"}, headers=auth_headers)
    client.post("/api/tasks", json={"description": "Fix the car"}, headers=auth_headers)

    resp = client.get("/api/tasks/search?q=groceries", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert "groceries" in data["tasks"][0]["description"].lower()


def test_search_by_priority(client, auth_headers):
    client.post("/api/tasks", json={"description": "Low prio", "priority": "low"}, headers=auth_headers)
    client.post("/api/tasks", json={"description": "High prio", "priority": "high"}, headers=auth_headers)

    resp = client.get("/api/tasks/search?priority=high", headers=auth_headers)
    assert resp.status_code == 200
    assert all(t["priority"] == "high" for t in resp.json()["tasks"])


def test_toggle_preserves_advanced_fields(client, auth_headers):
    resp = client.post(
        "/api/tasks",
        json={"description": "Toggle me", "priority": "high", "tags": ["test"]},
        headers=auth_headers,
    )
    task_id = resp.json()["id"]

    resp = client.patch(f"/api/tasks/{task_id}/toggle", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["is_complete"] is True
    assert resp.json()["priority"] == "high"
