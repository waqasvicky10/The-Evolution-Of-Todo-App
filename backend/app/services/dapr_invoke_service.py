"""
Dapr Service Invocation helper — Phase V.

Enables service-to-service calls through the Dapr sidecar.
Instead of hardcoding URLs, services call each other via:
  http://localhost:3500/v1.0/invoke/{app-id}/method/{endpoint}

Falls back to direct HTTP when Dapr is unavailable.
"""

import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"

_DIRECT_URLS: Dict[str, str] = {
    "todo-backend": os.getenv("BACKEND_URL", "http://localhost:8000"),
    "todo-frontend": os.getenv("FRONTEND_URL", "http://localhost:3000"),
}


def _dapr_ok() -> bool:
    if os.getenv("VERCEL") == "1":
        return False
    try:
        r = httpx.get(f"{DAPR_BASE_URL}/v1.0/healthz", timeout=0.3)
        return r.status_code in (200, 204)
    except Exception:
        return False


async def invoke(
    app_id: str,
    method: str,
    data: Optional[Dict[str, Any]] = None,
    verb: str = "POST",
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """
    Call another service via Dapr service invocation.

    Args:
        app_id: The Dapr app-id of the target service
        method: The HTTP path/method to call on the target
        data: JSON body (for POST/PUT)
        verb: HTTP verb (GET, POST, PUT, DELETE)
        timeout: Request timeout

    Returns:
        Dict with status, body, and source (dapr or direct)
    """
    if _dapr_ok():
        url = f"{DAPR_BASE_URL}/v1.0/invoke/{app_id}/method/{method}"
        source = "dapr"
    else:
        base = _DIRECT_URLS.get(app_id, f"http://{app_id}")
        url = f"{base}/{method.lstrip('/')}"
        source = "direct"

    try:
        async with httpx.AsyncClient() as client:
            if verb.upper() == "GET":
                resp = await client.get(url, timeout=timeout)
            elif verb.upper() == "DELETE":
                resp = await client.delete(url, timeout=timeout)
            elif verb.upper() == "PUT":
                resp = await client.put(url, json=data or {}, timeout=timeout)
            else:
                resp = await client.post(url, json=data or {}, timeout=timeout)

            body = None
            ct = resp.headers.get("content-type", "")
            if "json" in ct:
                body = resp.json()
            else:
                body = resp.text

            logger.info("[DaprInvoke] %s %s/%s → %d (%s)", verb, app_id, method, resp.status_code, source)
            return {"status": resp.status_code, "body": body, "source": source}

    except Exception as exc:
        logger.warning("[DaprInvoke] %s %s/%s failed: %s", verb, app_id, method, exc)
        return {"status": 0, "body": None, "source": source, "error": str(exc)}


async def invoke_backend(method: str, data: Optional[Dict] = None, verb: str = "POST") -> Dict[str, Any]:
    """Convenience: invoke the todo-backend service."""
    return await invoke("todo-backend", method, data, verb)


async def health_check(app_id: str) -> Dict[str, Any]:
    """Check if a service is reachable via Dapr."""
    return await invoke(app_id, "health", verb="GET")
