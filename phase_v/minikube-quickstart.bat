@echo off
REM Phase V - Minikube Quickstart for Windows
echo === Phase V: Minikube Quickstart ===

echo [1/6] Starting Minikube...
minikube start --driver=docker --memory=3072 --cpus=2

echo [2/6] Installing Dapr on cluster...
helm repo add dapr https://dapr.github.io/helm-charts/ 2>NUL
helm repo update
helm upgrade --install dapr dapr/dapr --namespace dapr-system --create-namespace --wait

echo [3/6] Applying Kubernetes secrets...
kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\secrets.yaml

echo [4/6] Deploying with Helm...
helm upgrade --install todo-app charts\todo-app ^
  --namespace todo-app ^
  --set secrets.dbConnectionString="sqlite:///./todo.db" ^
  --set secrets.secretKey="minikube-secret" ^
  --set secrets.openaiApiKey="mock" ^
  --set backend.env.MOCK_MODE="true" ^
  --wait --timeout 300s

echo [5/6] Verifying...
kubectl get pods -n todo-app
kubectl rollout status deployment/todo-backend -n todo-app --timeout=120s
kubectl rollout status deployment/todo-frontend -n todo-app --timeout=120s

echo [6/6] Port-forwarding...
start /B kubectl port-forward svc/todo-backend 8000:8000 -n todo-app
start /B kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app

echo.
echo === Phase V Minikube deployment complete! ===
echo Backend:  http://localhost:8000/health
echo Frontend: http://localhost:3000
pause
