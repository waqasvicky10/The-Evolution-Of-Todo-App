#!/usr/bin/env bash
# Phase V — kubectl-ai / kagent monitoring commands
set -euo pipefail

echo "=== Phase V: AI-Assisted Kubernetes Monitoring ==="

echo ""
echo "[1] Pod Status"
kubectl get pods -l app.kubernetes.io/instance=todo-app -o wide

echo ""
echo "[2] Dapr Components"
kubectl get components.dapr.io

echo ""
echo "[3] Backend Logs (last 20 lines)"
kubectl logs -l app.kubernetes.io/name=todo-backend --tail=20

echo ""
echo "[4] Dapr Sidecar Logs"
kubectl logs -l app.kubernetes.io/name=todo-backend -c daprd --tail=10 2>/dev/null || echo "No Dapr sidecar found"

echo ""
echo "[5] Redpanda Topics"
kubectl exec -it $(kubectl get pods -l app.kubernetes.io/name=redpanda -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "N/A") -- rpk topic list 2>/dev/null || echo "Redpanda not available"

echo ""
echo "[6] Resource Usage"
kubectl top pods -l app.kubernetes.io/instance=todo-app 2>/dev/null || echo "Metrics server not available"

echo ""
echo "=== Monitoring complete ==="
