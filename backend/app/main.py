"""
FastAPI application entry point — Phase V.

Main application instance with CORS, route registration, Dapr cron binding,
and event-driven integration.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import auth, tasks, chat
from app.api.routes.deployment import router as deployment_router
from app.api.routes.dapr_routes import router as dapr_router
from app.api.routes.advanced_features import router as features_router
from app.api.routes.master import router as master_router
from app.api.routes.kafka import (
    router as kafka_router,
    get_recurring_consumer,
    get_audit_consumer,
    get_realtime_consumer,
)
from app.routes import ai
from app.database import init_db
from app.services.reminder_service import process_due_reminders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Todo API - Phase V",
    description="Event-driven todo app with Dapr, Redpanda, advanced task management",
    version="5.0.0",
)


@app.get("/health")
def health():
    return {"status": "healthy", "phase": "V"}


@app.on_event("startup")
async def startup_event():
    logger.info("[Startup] Phase V server starting — initialising database tables")
    init_db()


# CORS — only needed when frontend calls backend directly (not via proxy)
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://the-evolution-of-todo-app-phase-iv.vercel.app",
]
if settings.CORS_ORIGINS:
    for o in settings.CORS_ORIGINS.split(","):
        o = o.strip()
        if o and o not in CORS_ORIGINS:
            CORS_ORIGINS.append(o)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(ai.router)
app.include_router(chat.router)
app.include_router(deployment_router)
app.include_router(kafka_router)
app.include_router(dapr_router)
app.include_router(features_router)
app.include_router(master_router)


# --- Dapr cron binding endpoint (reminder-cron) ---
@app.post("/reminder-cron")
async def dapr_cron_handler(request: Request):
    """Invoked by Dapr cron binding every 5 minutes to process due reminders."""
    count = await process_due_reminders()
    return {"processed": count}


# --- Dapr subscription endpoint (optional subscriber discovery) ---
@app.get("/dapr/subscribe")
def dapr_subscribe():
    return [
        {"pubsubname": "task-pubsub", "topic": "task-events", "route": "/events/task-events"},
        {"pubsubname": "task-pubsub", "topic": "reminders", "route": "/events/reminders"},
        {"pubsubname": "task-pubsub", "topic": "task-updates", "route": "/events/task-updates"},
        {"pubsubname": "task-pubsub", "topic": "recurring-tasks", "route": "/events/recurring-tasks"},
        {"pubsubname": "task-pubsub", "topic": "audit-log", "route": "/events/audit-log"},
    ]


@app.post("/events/task-events")
async def handle_task_events(request: Request):
    """Route task lifecycle events to RealTimeSyncConsumer + AuditLogConsumer."""
    body = await request.json()
    event_name = body.get("data", {}).get("event", "unknown")
    logger.info("[Event:task-events] Received: %s", event_name)

    await get_realtime_consumer().process_event(body)
    await get_audit_consumer().process_event(body)
    return {"status": "ok", "event": event_name}


@app.post("/events/reminders")
async def handle_reminders(request: Request):
    """Route reminder events to AuditLogConsumer."""
    body = await request.json()
    task_id = body.get("data", {}).get("task_id")
    logger.info("[Event:reminders] Received reminder for task %s", task_id)

    await get_audit_consumer().process_event(body)
    return {"status": "ok", "task_id": task_id}


@app.post("/events/task-updates")
async def handle_task_updates(request: Request):
    """Route partial-update events to RealTimeSyncConsumer + AuditLogConsumer."""
    body = await request.json()
    event_name = body.get("data", {}).get("event", "unknown")
    logger.info("[Event:task-updates] Received: %s", event_name)

    await get_realtime_consumer().process_event(body)
    await get_audit_consumer().process_event(body)
    return {"status": "ok", "event": event_name}


@app.post("/events/recurring-tasks")
async def handle_recurring_tasks(request: Request):
    """Route recurring-task events to RecurringTaskConsumer."""
    body = await request.json()
    task_id = body.get("data", {}).get("task_id")
    logger.info("[Event:recurring-tasks] Rescheduling task %s", task_id)

    result = await get_recurring_consumer().process_event(body)
    return {"status": "ok", "result": result}


@app.post("/events/audit-log")
async def handle_audit_log(request: Request):
    """Route audit events to AuditLogConsumer."""
    body = await request.json()
    logger.info("[Event:audit-log] Received: %s", body.get("data", {}).get("event", "unknown"))

    await get_audit_consumer().process_event(body)
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "message": "Todo API Phase V",
        "version": "5.0.0",
        "status": "running",
        "features": [
            "advanced-tasks",
            "event-driven",
            "dapr-integration",
            "redpanda-pubsub",
            "cron-reminders",
            "deployment-agent",
            "kafka-agent",
            "dapr-agent",
            "dapr-state-store",
            "dapr-service-invoke",
            "dapr-secrets",
            "recurring-tasks",
            "audit-log",
            "realtime-sync",
            "advanced-feature-agent",
            "recurring-auto-reschedule",
            "priority-levels",
            "tags-system",
            "search-filter-sort",
            "quick-commands",
            "master-orchestrator",
            "urdu-chatbot",
            "voice-commands",
            "reusable-intelligence",
            "12-test-scenarios",
            "kubectl-ai",
            "kagent",
        ],
    }
