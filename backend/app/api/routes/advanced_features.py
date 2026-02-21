"""
Advanced Features API — Phase V.

Exposes the AdvancedFeatureAgent for P+Q+P documentation,
feature matrix, chat command reference, and recurring calculations.
"""

from fastapi import APIRouter, Query
from typing import Any, Dict, List, Optional
from datetime import datetime

from ...agents.advanced_feature_agent import AdvancedFeatureAgent

router = APIRouter(prefix="/api/features", tags=["advanced-features"])

_agent = AdvancedFeatureAgent()


@router.get("/status")
def feature_status() -> Dict[str, Any]:
    """Return AdvancedFeatureAgent status and stats."""
    return _agent.get_status()


@router.get("/matrix")
def feature_matrix() -> Dict[str, Any]:
    """Return the complete Phase V feature matrix."""
    return _agent.get_feature_matrix()


@router.get("/chat-commands")
def chat_commands() -> List[Dict[str, str]]:
    """Return all Phase V chat commands the agent understands."""
    return _agent.get_chat_commands()


# ------------------------------------------------------------------
# P+Q+P explanations
# ------------------------------------------------------------------

@router.get("/explain/recurring")
def explain_recurring() -> Dict[str, Any]:
    step = _agent.explain_recurring()
    return {"problem": step.problem, "question": step.question, "pattern": step.pattern, "success": step.success}


@router.get("/explain/reminders")
def explain_reminders() -> Dict[str, Any]:
    step = _agent.explain_reminders()
    return {"problem": step.problem, "question": step.question, "pattern": step.pattern, "success": step.success}


@router.get("/explain/priorities")
def explain_priorities() -> Dict[str, Any]:
    step = _agent.explain_priorities()
    return {"problem": step.problem, "question": step.question, "pattern": step.pattern, "success": step.success}


@router.get("/explain/tags")
def explain_tags() -> Dict[str, Any]:
    step = _agent.explain_tags()
    return {"problem": step.problem, "question": step.question, "pattern": step.pattern, "success": step.success}


@router.get("/explain/search")
def explain_search() -> Dict[str, Any]:
    step = _agent.explain_search()
    return {"problem": step.problem, "question": step.question, "pattern": step.pattern, "success": step.success}


# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------

@router.get("/recurring/next-due")
def next_due_date(
    pattern: str = Query(..., pattern="^(daily|weekly|monthly)$"),
    current_due: Optional[str] = Query(None, description="ISO date of current due date"),
) -> Dict[str, Any]:
    """Calculate the next due date for a recurring pattern."""
    base = datetime.fromisoformat(current_due) if current_due else None
    return _agent.calculate_next_due(base, pattern)


@router.get("/pqp-trail")
def pqp_trail() -> List[Dict[str, Any]]:
    return _agent.get_audit_trail()
