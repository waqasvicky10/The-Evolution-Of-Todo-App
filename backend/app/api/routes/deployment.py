"""
Deployment API — Phase V.

Exposes the DeploymentAgent over REST endpoints.
All operations follow the P+Q+P pattern and return an audit trail.
"""

from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List

from ...agents.deployment_agent import DeploymentAgent, DeploymentState

router = APIRouter(prefix="/api/deployment", tags=["deployment"])

_agent = DeploymentAgent(dry_run=True)


@router.get("/status")
def deployment_status() -> Dict[str, Any]:
    """Return current deployment state and agent info."""
    s = _agent.state
    return {
        "cluster": s.cluster_name,
        "region": s.region,
        "namespace": s.namespace,
        "helm_release": s.helm_release,
        "backend_replicas": s.backend_replicas,
        "frontend_replicas": s.frontend_replicas,
        "dapr_installed": s.dapr_installed,
        "redpanda_enabled": s.redpanda_enabled,
        "total_steps_executed": len(s.steps),
    }


@router.post("/cluster")
def create_cluster() -> Dict[str, Any]:
    """P+Q+P: Create DOKS cluster."""
    step = _agent.create_cluster()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.post("/dapr")
def install_dapr() -> Dict[str, Any]:
    """P+Q+P: Install Dapr on cluster."""
    step = _agent.install_dapr()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.post("/deploy")
def deploy_app(image_tag: str = Query(default="latest")) -> Dict[str, Any]:
    """P+Q+P: Deploy the todo-app Helm chart."""
    step = _agent.deploy_app(image_tag=image_tag)
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.post("/verify")
def verify_deployment() -> Dict[str, Any]:
    """P+Q+P: Verify all pods are healthy."""
    step = _agent.verify_deployment()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.post("/scale")
def scale_component(component: str = Query(...), replicas: int = Query(..., ge=1, le=10)) -> Dict[str, Any]:
    """P+Q+P: Scale a deployment component."""
    step = _agent.scale(component=component, replicas=replicas)
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.post("/kubectl-ai")
def kubectl_ai_command(prompt: str = Query(...)) -> Dict[str, Any]:
    """P+Q+P: Execute an AI-assisted kubectl command."""
    step = _agent.kubectl_ai(prompt=prompt)
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.post("/kagent")
def kagent_check(check_type: str = Query(default="health")) -> Dict[str, Any]:
    """P+Q+P: Run a kagent monitoring check."""
    step = _agent.kagent_check(check_type=check_type)
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.get("/helm-status")
def helm_status() -> Dict[str, Any]:
    """P+Q+P: Get Helm release status."""
    step = _agent.get_helm_status()
    return {"problem": step.problem, "question": step.question, "commands": step.pattern, "result": step.result, "success": step.success}


@router.post("/full-deploy")
def full_deploy(image_tag: str = Query(default="latest")) -> Dict[str, Any]:
    """Run the complete deployment pipeline end-to-end."""
    return _agent.full_deploy(image_tag=image_tag)


@router.get("/audit-trail")
def audit_trail() -> List[Dict[str, Any]]:
    """Return the full P+Q+P audit trail for all executed steps."""
    return _agent.get_audit_trail()
