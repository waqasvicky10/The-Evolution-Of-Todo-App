"""
FastAPI application entry point.

Main application instance with CORS configuration and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import auth, tasks
from app.database import init_db


# Create FastAPI application
app = FastAPI(
    title="Todo API - Phase II",
    description="Multi-user todo application with authentication",
    version="2.0.0"
)


# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    init_db()


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    """
    Root endpoint.

    Returns:
        API information and status
    """
    return {
        "message": "Todo API Phase II",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy"}
