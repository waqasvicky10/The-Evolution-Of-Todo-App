# DeploymentAgent - Reusable Intelligence (P+Q+P)

## Problem
The Phase V todo app must be deployed to DigitalOcean Kubernetes (DOKS)
with Dapr sidecars, Redpanda, Helm charts, and CI/CD — all within a
$200 free credit, zero paid API keys.

## Question
How do we build a self-contained DeploymentAgent that:
- Creates and manages a DOKS cluster?
- Deploys via Helm (backend, frontend, Redpanda, Dapr components)?
- Uses kubectl-ai for AI-assisted operations?
- Uses kagent for monitoring and troubleshooting?
- Follows P+Q+P for every single operation (auditable)?
- Integrates with GitHub Actions CI/CD?

## Pattern

### Architecture
```
DeploymentAgent
  ├── create_cluster()     P+Q+P → doctl kubernetes create
  ├── install_dapr()       P+Q+P → helm install dapr
  ├── deploy_app()         P+Q+P → helm install todo-app
  ├── verify_deployment()  P+Q+P → kubectl get pods + rollout status
  ├── scale()              P+Q+P → kubectl scale
  ├── kubectl_ai()         P+Q+P → kubectl-ai "prompt"
  ├── kagent_check()       P+Q+P → kagent health/dapr/redpanda/logs
  ├── get_helm_status()    P+Q+P → helm status
  └── full_deploy()        Orchestrates all above end-to-end
```

### P+Q+P Record (every action)
```python
@dataclass
class PQPStep:
    problem: str         # What is the current state?
    question: str        # What action will solve this?
    pattern: List[str]   # Shell commands to execute
    result: str          # Output
    success: bool        # Did it work?
```

### Deployment Topology
```
DOKS Cluster ($200 credit, s-2vcpu-4gb x2)
├── Namespace: todo-app
│   ├── Deployment: todo-backend (2 replicas + Dapr sidecar)
│   ├── Deployment: todo-frontend (2 replicas)
│   ├── StatefulSet: redpanda (1 node, 2Gi)
│   └── Dapr Components: task-pubsub, task-statestore, reminder-cron
├── Namespace: dapr-system
│   └── Dapr control plane
└── Ingress: nginx
```

### CI/CD Integration (GitHub Actions)
1. Push to main → test backend + frontend
2. Build Docker images → push to GHCR
3. helm upgrade --install → DOKS cluster
4. kubectl rollout status → verify

### kubectl-ai Examples
- "deploy backend with 3 replicas" → kubectl scale deployment/todo-backend --replicas=3
- "show backend logs" → kubectl logs -l app.kubernetes.io/name=todo-backend --tail=50
- "check Dapr components" → kubectl get components.dapr.io
- "restart frontend" → kubectl rollout restart deployment/todo-frontend

### kagent Checks
- health: All pod status in todo-app namespace
- dapr: Dapr system pods
- redpanda: Cluster health + topic list
- logs: Backend application logs

### Reusability
1. Copy `backend/app/agents/deployment_agent.py`
2. Change `DeploymentState` defaults (cluster name, region, namespace)
3. Update `charts/` Helm templates for your domain
4. The P+Q+P pattern and audit trail work for any DevOps agent

### Cost Control
- Node size: s-2vcpu-4gb ($24/mo each, 2 nodes = $48/mo)
- Within $200 credit: ~4 months of operation
- Redpanda local (no cloud cost)
- Mock AI (no OpenAI billing)
