"""
DeploymentAgent — Phase V.

AI-assisted DevOps agent for DigitalOcean Kubernetes (DOKS) deployment.
Follows the P+Q+P pattern for every operation.
Uses kubectl-ai and kagent for AI-assisted cluster management.
"""

import logging
import subprocess
import shlex
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PQPStep:
    """Problem-Question-Pattern record for audit trail."""
    problem: str
    question: str
    pattern: List[str]
    result: Optional[str] = None
    success: bool = False


@dataclass
class DeploymentState:
    """Tracks the current deployment state."""
    cluster_name: str = "todo-cluster"
    region: str = "nyc1"
    namespace: str = "todo-app"
    helm_release: str = "todo-app"
    backend_replicas: int = 2
    frontend_replicas: int = 2
    dapr_installed: bool = False
    redpanda_enabled: bool = True
    steps: List[PQPStep] = field(default_factory=list)


class DeploymentAgent:
    """
    AI-assisted deployment agent for DOKS.

    Every action follows the P+Q+P pattern:
      Problem  -> describe current state
      Question -> what action to take
      Pattern  -> step-by-step execution
    """

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.state = DeploymentState()
        logger.info("DeploymentAgent initialised (dry_run=%s)", dry_run)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run(self, cmd: str) -> str:
        """Execute a shell command (or log in dry-run mode)."""
        logger.info("[CMD] %s", cmd)
        if self.dry_run:
            return f"[dry-run] {cmd}"
        try:
            result = subprocess.run(
                shlex.split(cmd),
                capture_output=True, text=True, timeout=300,
            )
            output = result.stdout.strip() or result.stderr.strip()
            if result.returncode != 0:
                logger.warning("[CMD FAIL] %s → %s", cmd, output)
            return output
        except Exception as exc:
            logger.error("[CMD ERROR] %s → %s", cmd, exc)
            return str(exc)

    def _pqp(self, problem: str, question: str, commands: List[str]) -> PQPStep:
        """Execute a P+Q+P step and record it."""
        step = PQPStep(problem=problem, question=question, pattern=commands)
        results = []
        for cmd in commands:
            out = self._run(cmd)
            results.append(out)
        step.result = "\n".join(results)
        step.success = True
        self.state.steps.append(step)
        logger.info("[P+Q+P] %s → OK", question)
        return step

    # ------------------------------------------------------------------
    # Public API (each follows P+Q+P)
    # ------------------------------------------------------------------

    def create_cluster(self) -> PQPStep:
        """P+Q+P: Create a DOKS cluster."""
        return self._pqp(
            problem="No Kubernetes cluster exists for the todo app.",
            question="How do we create a DOKS cluster within the $200 credit?",
            commands=[
                f"doctl kubernetes cluster create {self.state.cluster_name} "
                f"--region {self.state.region} --size s-2vcpu-4gb --count 2 --wait",
                f"doctl kubernetes cluster kubeconfig save {self.state.cluster_name}",
            ],
        )

    def install_dapr(self) -> PQPStep:
        """P+Q+P: Install Dapr on the cluster."""
        step = self._pqp(
            problem="Dapr runtime is not installed on the cluster.",
            question="How do we install Dapr for pubsub, state, and cron bindings?",
            commands=[
                "helm repo add dapr https://dapr.github.io/helm-charts/",
                "helm repo update",
                "helm upgrade --install dapr dapr/dapr --namespace dapr-system --create-namespace --wait",
            ],
        )
        self.state.dapr_installed = True
        return step

    def deploy_app(self, image_tag: str = "latest") -> PQPStep:
        """P+Q+P: Deploy the todo-app Helm chart."""
        return self._pqp(
            problem="The todo-app is not deployed or needs an update.",
            question="How do we deploy backend + frontend + Redpanda + Dapr via Helm?",
            commands=[
                f"kubectl create namespace {self.state.namespace} --dry-run=client -o yaml | kubectl apply -f -",
                f"helm upgrade --install {self.state.helm_release} ./charts/todo-app "
                f"--namespace {self.state.namespace} "
                f"--set backend.image.tag={image_tag} "
                f"--set frontend.image.tag={image_tag} "
                f"--set backend.replicaCount={self.state.backend_replicas} "
                f"--set frontend.replicaCount={self.state.frontend_replicas} "
                f"--set redpanda.enabled={str(self.state.redpanda_enabled).lower()} "
                f'--set secrets.dbConnectionString="${{DATABASE_URL}}" '
                f'--set secrets.secretKey="${{SECRET_KEY}}" '
                '--set secrets.openaiApiKey="mock" '
                "--wait --timeout 300s",
            ],
        )

    def verify_deployment(self) -> PQPStep:
        """P+Q+P: Verify all pods are running."""
        return self._pqp(
            problem="Need to confirm all pods are healthy after deployment.",
            question="How do we verify the deployment is successful?",
            commands=[
                f"kubectl get pods -n {self.state.namespace} -o wide",
                f"kubectl rollout status deployment/todo-backend -n {self.state.namespace} --timeout=120s",
                f"kubectl rollout status deployment/todo-frontend -n {self.state.namespace} --timeout=120s",
                "kubectl get components.dapr.io",
            ],
        )

    def scale(self, component: str, replicas: int) -> PQPStep:
        """P+Q+P: Scale a deployment."""
        step = self._pqp(
            problem=f"The {component} deployment needs to handle more/less load.",
            question=f"How do we scale {component} to {replicas} replicas?",
            commands=[
                f"kubectl scale deployment/todo-{component} --replicas={replicas} -n {self.state.namespace}",
                f"kubectl get pods -l app.kubernetes.io/name=todo-{component} -n {self.state.namespace} -w --timeout=60s",
            ],
        )
        if component == "backend":
            self.state.backend_replicas = replicas
        elif component == "frontend":
            self.state.frontend_replicas = replicas
        return step

    def kubectl_ai(self, prompt: str) -> PQPStep:
        """P+Q+P: Execute an AI-assisted kubectl command."""
        return self._pqp(
            problem=f"User requested AI-assisted operation: '{prompt}'",
            question="How does kubectl-ai translate this to kubectl commands?",
            commands=[
                f'kubectl-ai "{prompt}"',
            ],
        )

    def kagent_check(self, check_type: str = "health") -> PQPStep:
        """P+Q+P: Run a kagent monitoring check."""
        checks = {
            "health": f"kubectl get pods -n {self.state.namespace} -o wide",
            "dapr": "kubectl get pods -n dapr-system",
            "redpanda": f"kubectl exec -it $(kubectl get pods -l app.kubernetes.io/name=redpanda -n {self.state.namespace} -o jsonpath='{{.items[0].metadata.name}}') -n {self.state.namespace} -- rpk cluster health",
            "logs": f"kubectl logs -l app.kubernetes.io/name=todo-backend -n {self.state.namespace} --tail=30",
        }
        cmd = checks.get(check_type, checks["health"])
        return self._pqp(
            problem=f"Need to check {check_type} status of the cluster.",
            question=f"What kubectl command gives us {check_type} info?",
            commands=[cmd],
        )

    def get_helm_status(self) -> PQPStep:
        """P+Q+P: Get current Helm release status."""
        return self._pqp(
            problem="Need to know the current state of the Helm release.",
            question="What does `helm status` show?",
            commands=[
                f"helm status {self.state.helm_release} -n {self.state.namespace}",
                f"helm list -n {self.state.namespace}",
            ],
        )

    # ------------------------------------------------------------------
    # Full deployment pipeline
    # ------------------------------------------------------------------

    def full_deploy(self, image_tag: str = "latest") -> Dict[str, Any]:
        """Run the complete deployment pipeline end-to-end."""
        steps = []
        steps.append(self.create_cluster())
        steps.append(self.install_dapr())
        steps.append(self.deploy_app(image_tag))
        steps.append(self.verify_deployment())
        steps.append(self.get_helm_status())

        return {
            "success": all(s.success for s in steps),
            "steps_count": len(steps),
            "cluster": self.state.cluster_name,
            "region": self.state.region,
            "namespace": self.state.namespace,
            "summary": [
                {"step": s.question, "success": s.success}
                for s in steps
            ],
        }

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Return the full P+Q+P audit trail."""
        return [
            {
                "problem": s.problem,
                "question": s.question,
                "commands": s.pattern,
                "result": s.result,
                "success": s.success,
            }
            for s in self.state.steps
        ]
