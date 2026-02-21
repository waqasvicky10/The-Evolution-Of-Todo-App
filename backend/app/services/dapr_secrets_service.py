"""
Dapr Secrets service — Phase V.

Retrieves application secrets through the Dapr secrets API.
Supports two backends:
  - kubernetes: For DOKS deployment (K8s Secrets)
  - local-secrets: For Docker Compose dev (local file)

Falls back to os.environ when Dapr is unavailable.
"""

import logging
import os
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"

K8S_STORE = "kubernetes"
LOCAL_STORE = "local-secrets"


def _dapr_ok() -> bool:
    if os.getenv("VERCEL") == "1":
        return False
    try:
        r = httpx.get(f"{DAPR_BASE_URL}/v1.0/healthz", timeout=0.3)
        return r.status_code in (200, 204)
    except Exception:
        return False


async def get_secret(
    secret_name: str,
    store_name: Optional[str] = None,
    key: Optional[str] = None,
) -> Optional[str]:
    """
    Retrieve a secret via Dapr.

    Args:
        secret_name: The K8s Secret name (e.g. 'db-secret')
        store_name: Which secret store to use (default: auto-detect)
        key: Specific key within the secret (e.g. 'connection-string')

    Returns:
        The secret value, or None if not found
    """
    if store_name is None:
        store_name = K8S_STORE if os.getenv("KUBERNETES_SERVICE_HOST") else LOCAL_STORE

    if _dapr_ok():
        url = f"{DAPR_BASE_URL}/v1.0/secrets/{store_name}/{secret_name}"
        try:
            async with httpx.AsyncClient() as c:
                resp = await c.get(url, timeout=2.0)
                if resp.status_code == 200:
                    data = resp.json()
                    if key:
                        return data.get(key)
                    return data.get(secret_name) or next(iter(data.values()), None)
        except Exception as exc:
            logger.warning("[DaprSecrets] Fetch %s/%s failed: %s", store_name, secret_name, exc)

    # Fallback: environment variables
    env_key = key.upper().replace("-", "_") if key else secret_name.upper().replace("-", "_")
    fallback = os.getenv(env_key)
    if fallback:
        logger.info("[DaprSecrets:fallback] Using env var %s", env_key)
    return fallback


async def get_db_connection_string() -> Optional[str]:
    """Get the database connection string from secrets."""
    return await get_secret("db-secret", key="connection-string") or os.getenv("DATABASE_URL")


async def get_secret_key() -> Optional[str]:
    """Get the application SECRET_KEY."""
    return await get_secret("db-secret", key="secret-key") or os.getenv("SECRET_KEY")


async def get_openai_key() -> Optional[str]:
    """Get the OPENAI_API_KEY (always 'mock' in Phase V)."""
    return await get_secret("db-secret", key="openai-api-key") or os.getenv("OPENAI_API_KEY", "mock")


async def list_secrets(store_name: Optional[str] = None) -> Dict[str, Any]:
    """List available secrets (keys only, not values — for security)."""
    if store_name is None:
        store_name = K8S_STORE if os.getenv("KUBERNETES_SERVICE_HOST") else LOCAL_STORE

    if _dapr_ok():
        url = f"{DAPR_BASE_URL}/v1.0/secrets/{store_name}/bulk"
        try:
            async with httpx.AsyncClient() as c:
                resp = await c.get(url, timeout=2.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return {"store": store_name, "secrets": list(data.keys()), "count": len(data)}
        except Exception as exc:
            logger.warning("[DaprSecrets] List failed: %s", exc)

    return {"store": store_name, "secrets": [], "count": 0, "source": "unavailable"}
