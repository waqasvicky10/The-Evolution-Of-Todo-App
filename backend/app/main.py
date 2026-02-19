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


# CORS
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://the-evolution-of-todo-app-phase-iv.vercel.app",
]
if settings.CORS_ORIGINS:
    for origin in settings.CORS_ORIGINS.split(","):
        origin = origin.strip()
        if origin and origin not in cors_origins:
            cors_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(ai.router)
app.include_router(chat.router)


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
    ]


@app.post("/events/task-events")
async def handle_task_events(request: Request):
    """Process task lifecycle events from Redpanda via Dapr."""
    body = await request.json()
    logger.info("[Event:task-events] Received: %s", body.get("data", {}).get("event", "unknown"))
    return {"status": "ok"}


@app.post("/events/reminders")
async def handle_reminders(request: Request):
    body = await request.json()
    logger.info("[Event:reminders] Received reminder for task %s", body.get("data", {}).get("task_id"))
    return {"status": "ok"}


@app.post("/events/task-updates")
async def handle_task_updates(request: Request):
    body = await request.json()
    logger.info("[Event:task-updates] Received: %s", body.get("data", {}).get("event", "unknown"))
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
        ],
    }
