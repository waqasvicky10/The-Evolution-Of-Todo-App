"""
Dapr State Store service — Phase V.

Provides a thin abstraction over the Dapr state store HTTP API
for caching user preferences, session data, and task metadata.
Falls back to an in-memory dict when Dapr is unavailable.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
STATE_STORE_NAME = "task-statestore"

_fallback_store: Dict[str, Any] = {}


def _dapr_ok() -> bool:
    if os.getenv("VERCEL") == "1":
        return False
    try:
        r = httpx.get(f"{DAPR_BASE_URL}/v1.0/healthz", timeout=0.3)
        return r.status_code in (200, 204)
    except Exception:
        return False


async def save_state(key: str, value: Any, metadata: Optional[Dict[str, str]] = None) -> bool:
    """Save a key-value pair. Returns True on success."""
    if _dapr_ok():
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}"
        body: List[Dict[str, Any]] = [{"key": key, "value": value}]
        if metadata:
            body[0]["metadata"] = metadata
        try:
            async with httpx.AsyncClient() as c:
                r = await c.post(url, json=body, timeout=2.0)
                r.raise_for_status()
                logger.info("[DaprState] Saved key=%s", key)
                return True
        except Exception as exc:
            logger.warning("[DaprState] Save failed key=%s: %s", key, exc)

    _fallback_store[key] = value
    logger.info("[DaprState:fallback] Saved key=%s", key)
    return True


async def get_state(key: str) -> Optional[Any]:
    """Read a value by key. Returns None if not found."""
    if _dapr_ok():
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}/{key}"
        try:
            async with httpx.AsyncClient() as c:
                r = await c.get(url, timeout=2.0)
                if r.status_code == 200 and r.text:
                    return r.json()
                return None
        except Exception as exc:
            logger.warning("[DaprState] Get failed key=%s: %s", key, exc)

    return _fallback_store.get(key)


async def delete_state(key: str) -> bool:
    """Delete a key. Returns True on success."""
    if _dapr_ok():
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}/{key}"
        try:
            async with httpx.AsyncClient() as c:
                r = await c.delete(url, timeout=2.0)
                r.raise_for_status()
                logger.info("[DaprState] Deleted key=%s", key)
                return True
        except Exception as exc:
            logger.warning("[DaprState] Delete failed key=%s: %s", key, exc)

    _fallback_store.pop(key, None)
    return True


async def bulk_get(keys: List[str]) -> Dict[str, Any]:
    """Get multiple keys in one call."""
    if _dapr_ok():
        url = f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE_NAME}/bulk"
        try:
            async with httpx.AsyncClient() as c:
                r = await c.post(url, json={"keys": keys}, timeout=2.0)
                if r.status_code == 200:
                    return {item["key"]: item.get("data") for item in r.json()}
        except Exception as exc:
            logger.warning("[DaprState] Bulk get failed: %s", exc)

    return {k: _fallback_store.get(k) for k in keys}


# ---- High-level helpers ----

async def save_user_preference(user_id: int, pref_key: str, pref_value: Any) -> bool:
    return await save_state(f"user:{user_id}:pref:{pref_key}", pref_value)


async def get_user_preference(user_id: int, pref_key: str, default: Any = None) -> Any:
    result = await get_state(f"user:{user_id}:pref:{pref_key}")
    return result if result is not None else default


async def save_task_metadata(task_id: int, metadata: Dict[str, Any]) -> bool:
    return await save_state(f"task:{task_id}:meta", metadata)


async def get_task_metadata(task_id: int) -> Optional[Dict[str, Any]]:
    return await get_state(f"task:{task_id}:meta")
