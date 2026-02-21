"""
Dapr API — Phase V.

Exposes the DaprAgent and Dapr services over REST endpoints.
All operations follow the P+Q+P pattern and return an audit trail.
"""

from fastapi import APIRouter, Query
from typing import Any, Dict, List, Optional

from ...agents.dapr_agent import DaprAgent
from ...services import dapr_state_service, dapr_invoke_service, dapr_secrets_service

router = APIRouter(prefix="/api/dapr", tags=["dapr"])

_agent = DaprAgent(dry_run=True)


# ------------------------------------------------------------------
# Agent status & setup
# ------------------------------------------------------------------

@router.get("/status")
def dapr_status() -> Dict[str, Any]:
    """Return current Dapr agent state."""
    return _agent.get_status()


@router.post("/setup")
def dapr_full_setup(target: str = Query(default="k8s", pattern="^(k8s|local)$")) -> Dict[str, Any]:
    """P+Q+P: Run the complete Dapr setup pipeline."""
    return _agent.full_setup(target=target)


# ------------------------------------------------------------------
# Installation
# ------------------------------------------------------------------

@router.post("/install/k8s")
def install_k8s() -> Dict[str, Any]:
    step = _agent.install_dapr_k8s()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.post("/install/local")
def install_local() -> Dict[str, Any]:
    step = _agent.install_dapr_local()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


# ------------------------------------------------------------------
# Component management
# ------------------------------------------------------------------

@router.get("/components")
def list_components() -> Dict[str, Any]:
    step = _agent.list_components()
    return {
        "components": {k: {"type": v["type"], "description": v["description"]} for k, v in _agent.state.components.items()},
        "pqp": {"question": step.question, "commands": step.pattern, "success": step.success},
    }


@router.post("/components/apply")
def apply_components() -> Dict[str, Any]:
    step = _agent.apply_components()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.post("/components/verify")
def verify_components() -> Dict[str, Any]:
    step = _agent.verify_components()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


# ------------------------------------------------------------------
# Pub/Sub
# ------------------------------------------------------------------

@router.post("/publish")
async def publish_event(topic: str = Query(...), data: str = Query(..., description="JSON string")) -> Dict[str, Any]:
    import json
    parsed = json.loads(data)
    step = await _agent.publish(topic, parsed)
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "success": step.success}


# ------------------------------------------------------------------
# State Store
# ------------------------------------------------------------------

@router.post("/state")
async def save_state(key: str = Query(...), value: str = Query(...)) -> Dict[str, Any]:
    import json
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        parsed = value
    ok = await dapr_state_service.save_state(key, parsed)
    return {"key": key, "saved": ok}


@router.get("/state/{key}")
async def get_state(key: str) -> Dict[str, Any]:
    val = await dapr_state_service.get_state(key)
    return {"key": key, "value": val, "found": val is not None}


@router.delete("/state/{key}")
async def delete_state(key: str) -> Dict[str, Any]:
    ok = await dapr_state_service.delete_state(key)
    return {"key": key, "deleted": ok}


# ------------------------------------------------------------------
# Service Invocation
# ------------------------------------------------------------------

@router.post("/invoke")
async def invoke_service(
    app_id: str = Query(...),
    method: str = Query(...),
    verb: str = Query(default="GET"),
) -> Dict[str, Any]:
    return await dapr_invoke_service.invoke(app_id, method, verb=verb)


@router.get("/invoke/health/{app_id}")
async def invoke_health(app_id: str) -> Dict[str, Any]:
    return await dapr_invoke_service.health_check(app_id)


# ------------------------------------------------------------------
# Secrets
# ------------------------------------------------------------------

@router.get("/secrets/{secret_name}")
async def get_secret(
    secret_name: str,
    store: Optional[str] = Query(default=None),
    key: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    val = await dapr_secrets_service.get_secret(secret_name, store_name=store, key=key)
    return {"secret": secret_name, "found": val is not None, "has_value": bool(val)}


@router.get("/secrets")
async def list_secrets(store: Optional[str] = Query(default=None)) -> Dict[str, Any]:
    return await dapr_secrets_service.list_secrets(store_name=store)


@router.post("/secrets/verify")
def verify_secrets() -> Dict[str, Any]:
    step = _agent.verify_secrets()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


# ------------------------------------------------------------------
# Sidecar management
# ------------------------------------------------------------------

@router.post("/sidecar/configure")
def configure_sidecar(app_id: str = Query(...), app_port: int = Query(...)) -> Dict[str, Any]:
    step = _agent.configure_sidecar(app_id, app_port)
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.get("/sidecar/health")
def sidecar_health() -> Dict[str, Any]:
    step = _agent.check_sidecar_health()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


# ------------------------------------------------------------------
# P+Q+P audit trail
# ------------------------------------------------------------------

@router.get("/pqp-trail")
def pqp_audit_trail() -> List[Dict[str, Any]]:
    return _agent.get_audit_trail()
