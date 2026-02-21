#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Phase V — Minikube + Helm Local Quickstart
#
# Prerequisites: minikube, kubectl, helm, docker
# Cost: $0 (local only)
# ============================================================================

echo "=== Phase V: Minikube Local Deployment ==="

# Step 1: Start Minikube
echo "[1/7] Starting Minikube (docker driver, 3072mb)..."
minikube start --driver=docker --memory=3072 --cpus=2 2>/dev/null || true
minikube status

# Step 2: Create namespace
echo "[2/7] Creating todo-app namespace..."
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Apply secrets
echo "[3/7] Applying Kubernetes secrets..."
kubectl apply -f k8s/secrets.yaml -n todo-app

# Step 4: Install Dapr
echo "[4/7] Installing Dapr on Minikube..."
helm repo add dapr https://dapr.github.io/helm-charts/ 2>/dev/null || true
helm repo update
helm upgrade --install dapr dapr/dapr \
  --namespace dapr-system --create-namespace --wait \
  --timeout 120s

echo "Dapr pods:"
kubectl get pods -n dapr-system

# Step 5: Build local images
echo "[5/7] Building local Docker images..."
eval $(minikube docker-env)
docker build -t todo-backend:local -f docker/backend.Dockerfile ./backend
docker build -t todo-frontend:local -f frontend/frontend.Dockerfile ./frontend

# Step 6: Deploy with Helm
echo "[6/7] Deploying via Helm..."
helm upgrade --install todo-app ./charts/todo-app \
  --namespace todo-app \
  --set backend.image.repository=todo-backend \
  --set backend.image.tag=local \
  --set backend.image.pullPolicy=Never \
  --set frontend.image.repository=todo-frontend \
  --set frontend.image.tag=local \
  --set frontend.image.pullPolicy=Never \
  --set secrets.dbConnectionString="${DATABASE_URL:-sqlite:///./todo.db}" \
  --set secrets.secretKey="${SECRET_KEY:-minikube-dev-key}" \
  --set secrets.openaiApiKey="mock" \
  --wait --timeout 300s

# Step 7: Verify
echo "[7/7] Verifying deployment..."
kubectl get pods -n todo-app -o wide
kubectl rollout status deployment/todo-backend -n todo-app --timeout=120s
kubectl rollout status deployment/todo-frontend -n todo-app --timeout=120s

echo ""
echo "=== Deployment complete ==="
echo ""

# Get service URLs
BACKEND_URL=$(minikube service todo-backend -n todo-app --url 2>/dev/null || echo "pending")
FRONTEND_URL=$(minikube service todo-frontend -n todo-app --url 2>/dev/null || echo "pending")

echo "Backend:  $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo ""
echo "Useful commands:"
echo "  kubectl get pods -n todo-app"
echo "  kubectl logs -l app.kubernetes.io/name=todo-backend -n todo-app"
echo "  kubectl-ai 'show all pods in todo-app namespace'"
echo "  minikube dashboard"
echo ""
echo "To tear down:"
echo "  helm uninstall todo-app -n todo-app"
echo "  minikube stop"
