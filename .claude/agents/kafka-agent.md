# KafkaAgent — Reusable Intelligence (P+Q+P)

## Problem
Phase V requires an event-driven architecture for:
- Task lifecycle tracking (created, updated, deleted, completed)
- Reminder notifications via cron → pubsub
- Recurring task auto-rescheduling on completion
- Immutable audit log of all mutations
- Real-time sync feed for frontend polling

All of this must run on Redpanda (Kafka-compatible, free, local) with Dapr
providing the abstraction layer, and zero paid API keys.

## Question
How do we build a self-contained KafkaAgent that:
- Manages Kafka topics (create, list, describe, delete)?
- Publishes events via Dapr pubsub (or falls back to logging)?
- Runs consumer services for recurring, audit, and real-time sync?
- Follows P+Q+P for every operation (auditable)?
- Integrates with the existing event_service.py?

## Pattern

### Architecture
```
KafkaAgent (backend/app/agents/kafka_agent.py)
  ├── Topic Management
  │   ├── create_topics()         → rpk topic create (5 topics)
  │   ├── list_topics()           → rpk topic list
  │   ├── describe_topic(name)    → rpk topic describe
  │   └── delete_topic(name)      → rpk topic delete
  ├── Event Publishing
  │   ├── publish_event(topic, data)  → Dapr HTTP or log fallback
  │   ├── emit_task_created()
  │   ├── emit_task_updated()
  │   ├── emit_task_deleted()
  │   ├── emit_task_completed()    → also triggers recurring-tasks
  │   ├── emit_reminder()
  │   └── emit_audit()
  ├── Cluster Health
  │   ├── check_cluster_health()   → rpk cluster health
  │   └── check_dapr_pubsub()     → Dapr healthz + metadata
  └── full_setup()                → end-to-end pipeline
```

### Topics (5 total)
| Topic | Partitions | Retention | Purpose |
|-------|-----------|-----------|---------|
| task-events | 3 | 7 days | Lifecycle events (created/updated/deleted/completed) |
| reminders | 1 | 1 day | Reminder notifications from cron binding |
| task-updates | 3 | 3 days | Partial update events for UI sync |
| audit-log | 1 | 30 days | Immutable audit trail of all mutations |
| recurring-tasks | 1 | 3 days | Completed recurring tasks needing reschedule |

### Consumer Services
```
backend/app/services/consumers/
  ├── __init__.py
  ├── recurring_consumer.py   → RecurringTaskConsumer
  │   - Listens: recurring-tasks topic
  │   - Action: auto-create next task with shifted due_date
  │   - Patterns: daily (+1d), weekly (+7d), monthly (+30d)
  ├── audit_consumer.py       → AuditLogConsumer
  │   - Listens: audit-log topic
  │   - Action: append to in-memory log (max 10K entries)
  │   - Query: by user_id, task_id, event_type
  └── realtime_consumer.py    → RealTimeSyncConsumer
      - Listens: task-events + task-updates topics
      - Action: per-user change feed (max 200 per user)
      - Frontend polls: GET /api/kafka/sync/{user_id}?since=<ISO>
```

### Event Flow
```
User Action → FastAPI Route → task_service
    ↓
event_service.py → publish_event(topic, data)
    ↓
Dapr Sidecar → Redpanda Broker
    ↓                           ↓                      ↓
task-events topic          audit-log topic         recurring-tasks topic
    ↓                           ↓                      ↓
/events/task-events       AuditLogConsumer        RecurringTaskConsumer
    ↓                           ↓                      ↓
RealTimeSyncConsumer      Immutable log           New task created
    ↓                                                  ↓
Frontend poll             Query: /api/kafka/     task.created event
/api/kafka/sync/          audit-log                (loop back)
```

### Dapr Integration
```yaml
# dapr/components/pubsub-redpanda.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: task-pubsub
spec:
  type: pubsub.kafka
  metadata:
    - name: brokers
      value: "redpanda:9092"
    - name: consumerGroup
      value: "todo-app-group"
    - name: authType
      value: "none"
```

### Docker Compose
- `redpanda`: Kafka-compatible broker (512MB, ports 19092/18082)
- `redpanda-init`: One-shot container that creates all 5 topics on startup
- `redpanda-console`: Web UI at :8080 for topic monitoring
- `backend-dapr`: Sidecar connecting backend ↔ Redpanda

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/kafka/status | GET | Agent + consumer stats |
| /api/kafka/setup | POST | Full setup pipeline |
| /api/kafka/topics/create | POST | Create all topics |
| /api/kafka/topics | GET | List topics |
| /api/kafka/topics/{name} | GET | Describe topic |
| /api/kafka/health | GET | Cluster health check |
| /api/kafka/dapr-status | GET | Dapr pubsub connectivity |
| /api/kafka/consumers | GET | Consumer group status |
| /api/kafka/consumers/reset | POST | Reset consumer offset |
| /api/kafka/audit-log | GET | Query audit log |
| /api/kafka/sync/{user_id} | GET | Real-time sync feed |
| /api/kafka/sync/{user_id} | DELETE | Clear sync feed |
| /api/kafka/pqp-trail | GET | P+Q+P audit trail |

### Reusability
1. Copy `backend/app/agents/kafka_agent.py` + `backend/app/services/consumers/`
2. Update `TOPICS` dict for your domain events
3. Implement domain-specific consumers (recurring, audit, sync)
4. The P+Q+P pattern, Dapr abstraction, and fallback logging work for any event-driven app

### Cost
- Redpanda: 0 (local container, no cloud)
- Dapr: 0 (open source sidecar)
- Redpanda Console: 0 (free UI)
- Total Kafka cost: $0
