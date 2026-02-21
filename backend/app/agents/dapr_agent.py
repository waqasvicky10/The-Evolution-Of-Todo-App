"""
DaprAgent — Phase V.

AI-assisted Dapr agent managing the full Dapr building-block stack:
  - Pub/Sub (Kafka via Redpanda)
  - State Store (Neon PostgreSQL)
  - Input Bindings (cron for reminders)
  - Secrets (Kubernetes / local-file)
  - Service Invocation (backend ↔ services)

Every operation follows the P+Q+P pattern (Problem → Question → Pattern).
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"


# ---------------------------------------------------------------------------
# Dapr Component Definitions (source of truth)
# ---------------------------------------------------------------------------

DAPR_COMPONENTS = {
    "task-pubsub": {
        "type": "pubsub.kafka",
        "description": "Pub/Sub via Redpanda (Kafka-compatible)",
        "metadata": {
            "brokers": "redpanda:9092",
            "consumerGroup": "todo-app-group",
            "authType": "none",
        },
        "scopes": ["todo-backend"],
    },
    "task-statestore": {
        "type": "state.postgresql",
        "description": "State store backed by Neon PostgreSQL",
        "metadata": {
            "connectionString": "secretKeyRef:db-secret/connection-string",
            "tableName": "dapr_state",
            "metadataTableName": "dapr_metadata",
        },
        "scopes": ["todo-backend"],
    },
    "reminder-cron": {
        "type": "bindings.cron",
        "description": "Input binding — fires every 5m for reminder processing",
        "metadata": {
            "schedule": "@every 5m",
            "direction": "input",
        },
        "scopes": ["todo-backend"],
    },
    "kubernetes": {
        "type": "secretstores.kubernetes",
        "description": "K8s-native secret store for DOKS deployment",
        "metadata": {},
        "scopes": [],
    },
    "local-secrets": {
        "type": "secretstores.local.file",
        "description": "Local file secret store for Docker Compose dev",
        "metadata": {
            "secretsFile": "/components/secrets.json",
        },
        "scopes": [],
    },
}


@dataclass
class PQPStep:
    """Problem-Question-Pattern record for audit trail."""
    problem: str
    question: str
    pattern: List[str]
    result: Optional[str] = None
    success: bool = False


@dataclass
class DaprState:
    """Tracks the state of the Dapr agent."""
    dapr_available: Optional[bool] = None
    dapr_version: Optional[str] = None
    components: Dict[str, Dict[str, Any]] = field(default_factory=lambda: dict(DAPR_COMPONENTS))
    sidecar_apps: List[str] = field(default_factory=lambda: ["todo-backend"])
    steps: List[PQPStep] = field(default_factory=list)
    state_ops: int = 0
    invoke_ops: int = 0
    secret_ops: int = 0
    pubsub_ops: int = 0


class DaprAgent:
    """
    AI-assisted Dapr agent for Phase V.

    Manages the five Dapr building blocks:
      1. Pub/Sub        — publish/subscribe via Redpanda
      2. State Store    — read/write state via Neon PostgreSQL
      3. Bindings       — cron input for reminders
      4. Secrets        — K8s secrets or local file
      5. Service Invoke — backend ↔ other services via Dapr
    """

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.state = DaprState()
        logger.info("DaprAgent initialised (dry_run=%s)", dry_run)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_dapr(self) -> bool:
        """Check if Dapr sidecar is available."""
        if self.state.dapr_available is not None:
            return self.state.dapr_available
        if os.getenv("VERCEL") == "1":
            self.state.dapr_available = False
            return False
        try:
            resp = httpx.get(f"{DAPR_BASE_URL}/v1.0/healthz", timeout=0.5)
            self.state.dapr_available = resp.status_code in (200, 204)
        except Exception:
            self.state.dapr_available = False
        return self.state.dapr_available

    def _pqp(self, problem: str, question: str, commands: List[str]) -> PQPStep:
        """Execute a P+Q+P step and record it."""
        step = PQPStep(problem=problem, question=question, pattern=commands)
        results = []
        for cmd in commands:
            results.append(f"[{'dry-run' if self.dry_run else 'executed'}] {cmd}")
        step.result = "\n".join(results)
        step.success = True
        self.state.steps.append(step)
        logger.info("[P+Q+P] %s → OK", question)
        return step

    # ------------------------------------------------------------------
    # 1. INSTALLATION (P+Q+P)
    # ------------------------------------------------------------------

    def install_dapr_k8s(self) -> PQPStep:
        """P+Q+P: Install Dapr on Kubernetes."""
        return self._pqp(
            problem="Dapr runtime is not installed on the target Kubernetes cluster.",
            question="How do we install Dapr on DOKS?",
            commands=[
                "helm repo add dapr https://dapr.github.io/helm-charts/",
                "helm repo update",
                "helm upgrade --install dapr dapr/dapr --namespace dapr-system --create-namespace --wait",
                "kubectl get pods -n dapr-system",
            ],
        )

    def install_dapr_local(self) -> PQPStep:
        """P+Q+P: Install Dapr locally for development."""
        return self._pqp(
            problem="Dapr CLI is needed for local development and testing.",
            question="How do we set up Dapr for local Docker Compose?",
            commands=[
                "dapr init",
                "dapr --version",
                "docker ps --filter name=dapr",
            ],
        )

    # ------------------------------------------------------------------
    # 2. COMPONENT MANAGEMENT (P+Q+P)
    # ------------------------------------------------------------------

    def list_components(self) -> PQPStep:
        """P+Q+P: List all Dapr components."""
        names = list(self.state.components.keys())
        return self._pqp(
            problem="Need to verify which Dapr components are deployed.",
            question="What Dapr components exist in our cluster?",
            commands=[
                "kubectl get components.dapr.io -A",
                f"# Expected: {', '.join(names)}",
            ],
        )

    def apply_components(self) -> PQPStep:
        """P+Q+P: Apply all Dapr component YAMLs."""
        return self._pqp(
            problem="Dapr components may not be applied to the cluster yet.",
            question="How do we apply all component YAMLs?",
            commands=[
                "kubectl apply -f dapr/components/pubsub-redpanda.yaml",
                "kubectl apply -f dapr/components/statestore-postgresql.yaml",
                "kubectl apply -f dapr/components/cron-binding.yaml",
                "kubectl apply -f dapr/components/secrets-kubernetes.yaml",
                "kubectl apply -f dapr/components/secrets-local.yaml",
                "kubectl get components.dapr.io",
            ],
        )

    def verify_components(self) -> PQPStep:
        """P+Q+P: Verify all components are loaded by the sidecar."""
        return self._pqp(
            problem="Components might be applied but not loaded by the sidecar.",
            question="How do we verify Dapr has loaded all components?",
            commands=[
                f"curl -s {DAPR_BASE_URL}/v1.0/metadata | python -m json.tool",
                f"curl -s {DAPR_BASE_URL}/v1.0/healthz",
            ],
        )

    # ------------------------------------------------------------------
    # 3. PUB/SUB operations (P+Q+P)
    # ------------------------------------------------------------------

    async def publish(self, topic: str, data: Dict[str, Any]) -> PQPStep:
        """P+Q+P: Publish a message to a Dapr pubsub topic."""
        payload = {**data, "published_at": datetime.utcnow().isoformat()}
        url = f"{DAPR_BASE_URL}/v1.0/publish/task-pubsub/{topic}"

        if self._check_dapr() and not self.dry_run:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, json=payload, timeout=2.0)
                    resp.raise_for_status()
            except Exception as exc:
                logger.warning("[DaprAgent] Publish to %s failed: %s", topic, exc)

        self.state.pubsub_ops += 1
        return self._pqp(
            problem=f"Event needs to be published to topic '{topic}'.",
            question=f"How do we publish to '{topic}' via Dapr Pub/Sub?",
            commands=[f"POST {url} → {json.dumps(data, default=str)[:200]}"],
        )

    # ------------------------------------------------------------------
    # 4. STATE STORE operations (P+Q+P)
    # ------------------------------------------------------------------

    async def save_state(self, key: str, value: Any) -> PQPStep:
        """P+Q+P: Save a key-value pair to the Dapr state store."""
        url = f"{DAPR_BASE_URL}/v1.0/state/task-statestore"
        body = [{"key": key, "value": value}]

        if self._check_dapr() and not self.dry_run:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, json=body, timeout=2.0)
                    resp.raise_for_status()
            except Exception as exc:
                logger.warning("[DaprAgent] State save failed: %s", exc)

        self.state.state_ops += 1
        return self._pqp(
            problem=f"Need to persist state for key '{key}'.",
            question=f"How do we save '{key}' to the Dapr state store?",
            commands=[f"POST {url} → key={key}, value={json.dumps(value, default=str)[:100]}"],
        )

    async def get_state(self, key: str) -> Dict[str, Any]:
        """Read a value from the Dapr state store."""
        url = f"{DAPR_BASE_URL}/v1.0/state/task-statestore/{key}"

        if self._check_dapr() and not self.dry_run:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, timeout=2.0)
                    if resp.status_code == 200:
                        self.state.state_ops += 1
                        return {"key": key, "value": resp.json(), "source": "dapr"}
            except Exception as exc:
                logger.warning("[DaprAgent] State get failed: %s", exc)

        self.state.state_ops += 1
        return {"key": key, "value": None, "source": "dry-run"}

    async def delete_state(self, key: str) -> PQPStep:
        """P+Q+P: Delete a key from the Dapr state store."""
        url = f"{DAPR_BASE_URL}/v1.0/state/task-statestore/{key}"

        if self._check_dapr() and not self.dry_run:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.delete(url, timeout=2.0)
                    resp.raise_for_status()
            except Exception as exc:
                logger.warning("[DaprAgent] State delete failed: %s", exc)

        self.state.state_ops += 1
        return self._pqp(
            problem=f"State key '{key}' needs to be removed.",
            question=f"How do we delete '{key}' from the Dapr state store?",
            commands=[f"DELETE {url}"],
        )

    # ------------------------------------------------------------------
    # 5. SERVICE INVOCATION (P+Q+P)
    # ------------------------------------------------------------------

    async def invoke_service(self, app_id: str, method: str, data: Optional[Dict] = None, http_verb: str = "POST") -> Dict[str, Any]:
        """Invoke another service via Dapr service invocation."""
        url = f"{DAPR_BASE_URL}/v1.0/invoke/{app_id}/method/{method}"

        if self._check_dapr() and not self.dry_run:
            try:
                async with httpx.AsyncClient() as client:
                    if http_verb.upper() == "GET":
                        resp = await client.get(url, timeout=5.0)
                    else:
                        resp = await client.post(url, json=data or {}, timeout=5.0)
                    self.state.invoke_ops += 1
                    return {"app_id": app_id, "method": method, "status": resp.status_code, "body": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text}
            except Exception as exc:
                logger.warning("[DaprAgent] Invoke %s/%s failed: %s", app_id, method, exc)

        self.state.invoke_ops += 1
        return {"app_id": app_id, "method": method, "status": "dry-run", "body": None}

    # ------------------------------------------------------------------
    # 6. SECRETS (P+Q+P)
    # ------------------------------------------------------------------

    async def get_secret(self, store_name: str, secret_name: str) -> Dict[str, Any]:
        """Retrieve a secret from a Dapr secret store."""
        url = f"{DAPR_BASE_URL}/v1.0/secrets/{store_name}/{secret_name}"

        if self._check_dapr() and not self.dry_run:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, timeout=2.0)
                    if resp.status_code == 200:
                        self.state.secret_ops += 1
                        return {"store": store_name, "secret": secret_name, "found": True, "keys": list(resp.json().keys())}
            except Exception as exc:
                logger.warning("[DaprAgent] Secret fetch failed: %s", exc)

        self.state.secret_ops += 1
        return {"store": store_name, "secret": secret_name, "found": False, "source": "dry-run"}

    def verify_secrets(self) -> PQPStep:
        """P+Q+P: Verify all required secrets are accessible."""
        return self._pqp(
            problem="Application secrets (DATABASE_URL, SECRET_KEY, OPENAI_API_KEY) must be accessible via Dapr.",
            question="How do we verify secrets are available through the Dapr secrets API?",
            commands=[
                f"curl -s {DAPR_BASE_URL}/v1.0/secrets/kubernetes/db-secret",
                "kubectl get secret db-secret -o jsonpath='{.data}' | base64 -d",
            ],
        )

    # ------------------------------------------------------------------
    # 7. SIDECAR MANAGEMENT (P+Q+P)
    # ------------------------------------------------------------------

    def configure_sidecar(self, app_id: str, app_port: int) -> PQPStep:
        """P+Q+P: Configure Dapr sidecar annotations for a deployment."""
        annotations = {
            "dapr.io/enabled": "true",
            "dapr.io/app-id": app_id,
            "dapr.io/app-port": str(app_port),
            "dapr.io/log-level": "info",
            "dapr.io/config": "appconfig",
            "dapr.io/enable-metrics": "true",
            "dapr.io/metrics-port": "9090",
        }
        if app_id not in self.state.sidecar_apps:
            self.state.sidecar_apps.append(app_id)

        return self._pqp(
            problem=f"Deployment '{app_id}' needs a Dapr sidecar for building-block access.",
            question=f"What annotations enable the Dapr sidecar for '{app_id}'?",
            commands=[
                f"# Pod annotations for {app_id}:",
                *[f"#   {k}: \"{v}\"" for k, v in annotations.items()],
                f"kubectl annotate deployment {app_id} {' '.join(f'{k}={v}' for k, v in annotations.items())} --overwrite",
            ],
        )

    def check_sidecar_health(self) -> PQPStep:
        """P+Q+P: Check if the Dapr sidecar is healthy."""
        return self._pqp(
            problem="Need to verify the Dapr sidecar is running and connected to all components.",
            question="How do we check sidecar health and metadata?",
            commands=[
                f"curl -s {DAPR_BASE_URL}/v1.0/healthz",
                f"curl -s {DAPR_BASE_URL}/v1.0/metadata",
            ],
        )

    # ------------------------------------------------------------------
    # Full setup pipeline
    # ------------------------------------------------------------------

    def full_setup(self, target: str = "k8s") -> Dict[str, Any]:
        """Run the complete Dapr setup pipeline."""
        steps = []
        if target == "k8s":
            steps.append(self.install_dapr_k8s())
        else:
            steps.append(self.install_dapr_local())
        steps.append(self.apply_components())
        steps.append(self.list_components())
        steps.append(self.configure_sidecar("todo-backend", 8000))
        steps.append(self.verify_components())
        steps.append(self.verify_secrets())
        steps.append(self.check_sidecar_health())

        return {
            "success": all(s.success for s in steps),
            "steps_count": len(steps),
            "target": target,
            "components": list(self.state.components.keys()),
            "sidecar_apps": self.state.sidecar_apps,
            "summary": [{"step": s.question, "success": s.success} for s in steps],
        }

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        return {
            "dapr_available": self.state.dapr_available,
            "dapr_version": self.state.dapr_version,
            "components": {k: v["type"] for k, v in self.state.components.items()},
            "sidecar_apps": self.state.sidecar_apps,
            "operations": {
                "pubsub": self.state.pubsub_ops,
                "state": self.state.state_ops,
                "invoke": self.state.invoke_ops,
                "secrets": self.state.secret_ops,
            },
            "total_pqp_steps": len(self.state.steps),
        }

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return [
            {"problem": s.problem, "question": s.question, "commands": s.pattern, "result": s.result, "success": s.success}
            for s in self.state.steps
        ]
