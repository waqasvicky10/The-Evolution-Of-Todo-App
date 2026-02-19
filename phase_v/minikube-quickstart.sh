#!/usr/bin/env bash
# Phase V — Minikube Quickstart (local testing, zero payment)
set -euo pipefail

echo "=== Phase V: Minikube Quickstart ==="

# 1. Start Minikube
echo "[1/7] Starting Minikube..."
minikube start --driver=docker --memory=3072 --cpus=2

# 2. Install Dapr on cluster
echo "[2/7] Installing Dapr..."
helm repo add dapr https://dapr.github.io/helm-charts/ 2>/dev/null || true
helm repo update
helm upgrade --install dapr dapr/dapr --namespace dapr-system --create-namespace --wait

# 3. Build images inside Minikube's Docker
echo "[3/7] Building Docker images in Minikube..."
eval $(minikube docker-env)
docker build -t todo-backend:local -f docker/backend.Dockerfile backend/
docker build -t todo-frontend:local -f frontend/frontend.Dockerfile frontend/

# 4. Apply Kubernetes secrets
echo "[4/7] Applying secrets..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml

# 5. Deploy via Helm
echo "[5/7] Deploying with Helm..."
helm upgrade --install todo-app ./charts/todo-app \
  --namespace todo-app \
  --set backend.image.repository=todo-backend \
  --set backend.image.tag=local \
  --set backend.image.pullPolicy=Never \
  --set frontend.image.repository=todo-frontend \
  --set frontend.image.tag=local \
  --set frontend.image.pullPolicy=Never \
  --set redpanda.enabled=true \
  --set secrets.dbConnectionString="sqlite:///./todo.db" \
  --set secrets.secretKey="minikube-secret" \
  --set secrets.openaiApiKey="mock" \
  --wait --timeout 300s

# 6. Verify
echo "[6/7] Verifying deployment..."
kubectl get pods -n todo-app
kubectl rollout status deployment/todo-backend -n todo-app --timeout=120s
kubectl rollout status deployment/todo-frontend -n todo-app --timeout=120s

# 7. Port forward
echo "[7/7] Port-forwarding..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
kubectl port-forward svc/todo-backend 8000:8000 -n todo-app &
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app &

echo ""
echo "=== Phase V Minikube deployment complete! ==="
echo "Backend:  http://localhost:8000/health"
echo "Frontend: http://localhost:3000"
echo "Redpanda Console: kubectl port-forward svc/<release>-redpanda-console 8080:8080 -n todo-app"
wait
