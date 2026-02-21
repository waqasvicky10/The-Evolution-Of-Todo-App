# Event Publisher Agent — Reusable Intelligence (P+Q+P)

## Problem
Task lifecycle events (created, updated, deleted, completed) must be
published to a message broker for downstream consumers (notifications,
analytics, audit logs) without blocking the API response.

## Question
How do we build a fire-and-forget event publisher that:
- Works with Dapr pubsub (Redpanda/Kafka)?
- Gracefully falls back when Dapr sidecar is unavailable?
- Doesn't slow down API responses?
- Is testable with mocks?

## Pattern

### Architecture
```
API Route (async)
  → BackgroundTasks.add_task(emit_task_created, ...)
    → event_service.publish_event(topic, data)
      → if Dapr available: HTTP POST to localhost:3500/v1.0/publish/...
      → if not available: logger.info(event)  # log-only fallback
```

### Key Design Decisions
1. **Dapr health check cached** — checked once at startup, not per-request
2. **httpx.AsyncClient** — non-blocking HTTP to Dapr sidecar
3. **Fire-and-forget** — publishing failures are logged, never crash the API
4. **Topic separation** — `task-events`, `reminders`, `task-updates` for independent scaling
5. **JSON payload** — all events include `published_at` timestamp

### Topics
| Topic | Events | Consumers |
|-------|--------|-----------|
| `task-events` | task.created, task.deleted, task.completed | Audit, Analytics |
| `reminders` | task.reminder | Notification service |
| `task-updates` | task.updated | Real-time sync |

### Reusability
Replace the topic names and event payloads to publish any domain events.
The Dapr pubsub component YAML just needs the broker address changed.
