# DaprAgent — Reusable Intelligence (P+Q+P)

## Problem
Phase V needs a unified abstraction layer over:
- Pub/Sub (Redpanda/Kafka) — event publishing and subscription
- State Store (Neon PostgreSQL) — caching preferences, session data
- Input Bindings (cron) — periodic reminder processing
- Secrets (K8s Secrets / local file) — DATABASE_URL, SECRET_KEY, OPENAI_API_KEY
- Service Invocation — backend ↔ services without hardcoded URLs

Direct calls couple services together. Dapr provides location-transparent,
resilient building blocks with sidecar injection.

## Question
How do we build a self-contained DaprAgent that:
- Installs Dapr on DOKS or locally?
- Creates and manages all component YAMLs?
- Provides state store read/write/delete via HTTP?
- Enables service-to-service calls via Dapr invoke?
- Retrieves secrets without hardcoding them in code?
- Follows P+Q+P for every operation?

## Pattern

### Architecture — Five Building Blocks
```
DaprAgent (backend/app/agents/dapr_agent.py)
├── 1. PUB/SUB
│   ├── publish(topic, data)          → POST /v1.0/publish/task-pubsub/{topic}
│   └── subscribe (auto via /dapr/subscribe endpoint)
├── 2. STATE STORE
│   ├── save_state(key, value)        → POST /v1.0/state/task-statestore
│   ├── get_state(key)                → GET  /v1.0/state/task-statestore/{key}
│   ├── delete_state(key)             → DEL  /v1.0/state/task-statestore/{key}
│   └── bulk_get(keys)                → POST /v1.0/state/task-statestore/bulk
├── 3. BINDINGS
│   └── reminder-cron                 → Dapr calls POST /reminder-cron every 5m
├── 4. SECRETS
│   ├── get_secret(store, name, key)  → GET  /v1.0/secrets/{store}/{name}
│   └── list_secrets(store)           → GET  /v1.0/secrets/{store}/bulk
└── 5. SERVICE INVOCATION
    └── invoke(app_id, method, data)  → POST /v1.0/invoke/{app_id}/method/{method}
```

### Dapr Component YAMLs (6 files)
```
dapr/components/
├── pubsub-redpanda.yaml     → pubsub.kafka (Redpanda)
├── statestore-postgresql.yaml → state.postgresql (Neon)
├── cron-binding.yaml         → bindings.cron (@every 5m)
├── secrets-kubernetes.yaml   → secretstores.kubernetes (DOKS)
├── secrets-local.yaml        → secretstores.local.file (Docker Compose)
└── secrets.json              → Local dev secrets file
```

### Backend Services (3 files)
```
backend/app/services/
├── dapr_state_service.py     → save/get/delete/bulk + user prefs + task metadata
├── dapr_invoke_service.py    → invoke(app_id, method) with Dapr or direct fallback
└── dapr_secrets_service.py   → get_secret() with K8s or local or env fallback
```

### Helm Chart Integration
```yaml
# backend-deployment.yaml annotations
dapr.io/enabled: "true"
dapr.io/app-id: "todo-backend"
dapr.io/app-port: "8000"

# frontend-deployment.yaml annotations (new in Phase V)
dapr.io/enabled: "true"
dapr.io/app-id: "todo-frontend"
dapr.io/app-port: "3000"

# dapr-components.yaml includes:
# - task-pubsub (pubsub.kafka)
# - task-statestore (state.postgresql)
# - reminder-cron (bindings.cron)
# - kubernetes (secretstores.kubernetes)
```

### Docker Compose Sidecar
```yaml
backend-dapr:
  image: daprio/daprd:1.13.4
  command:
    - ./daprd
    - -app-id, todo-backend
    - -app-port, 8000
    - -dapr-http-port, 3500
    - -resources-path, /components
  volumes:
    - ./dapr/components:/components
  network_mode: "service:backend"
```

### Fallback Strategy (every service)
```
1. Check Dapr sidecar health: GET /v1.0/healthz
2. If available → use Dapr HTTP API
3. If unavailable (Vercel, local dev) →
   - State: in-memory dict
   - Invoke: direct HTTP to service URL
   - Secrets: os.environ fallback
   - Pub/Sub: logger.info() only
```

### API Endpoints (16 total)
| Endpoint | Method | Building Block |
|----------|--------|---------------|
| /api/dapr/status | GET | Agent status |
| /api/dapr/setup | POST | Full pipeline |
| /api/dapr/install/k8s | POST | Install on K8s |
| /api/dapr/install/local | POST | Install locally |
| /api/dapr/components | GET | List components |
| /api/dapr/components/apply | POST | Apply YAMLs |
| /api/dapr/components/verify | POST | Verify loaded |
| /api/dapr/publish | POST | Pub/Sub |
| /api/dapr/state | POST | State save |
| /api/dapr/state/{key} | GET | State read |
| /api/dapr/state/{key} | DELETE | State delete |
| /api/dapr/invoke | POST | Service invoke |
| /api/dapr/invoke/health/{id} | GET | Service health |
| /api/dapr/secrets/{name} | GET | Get secret |
| /api/dapr/secrets | GET | List secrets |
| /api/dapr/sidecar/configure | POST | Configure sidecar |
| /api/dapr/sidecar/health | GET | Sidecar health |
| /api/dapr/pqp-trail | GET | Audit trail |

### Reusability
1. Copy `backend/app/agents/dapr_agent.py` + `backend/app/services/dapr_*_service.py`
2. Copy `dapr/components/` and update broker/connection strings
3. Update Helm annotations for your service names
4. All fallback logic and P+Q+P pattern transfer to any Dapr project

### Cost
- Dapr: $0 (open source, sidecar injection)
- No additional infra — reuses existing Redpanda + Neon PostgreSQL
