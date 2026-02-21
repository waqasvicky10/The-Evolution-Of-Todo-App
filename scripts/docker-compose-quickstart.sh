#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Phase V — Docker Compose Local Dev Quickstart
#
# Prerequisites: docker, docker-compose
# Cost: $0 (everything local, mock OpenAI)
# ============================================================================

echo "=== Phase V: Docker Compose Local Dev ==="

# Step 1: Check .env
if [ ! -f .env ]; then
  echo "[1/4] Creating .env from .env.example..."
  cp .env.example .env 2>/dev/null || cat > .env <<'ENVEOF'
DATABASE_URL=sqlite:///./todo.db
SECRET_KEY=local-dev-secret-key-change-in-prod
BETTER_AUTH_SECRET=local-dev-secret
OPENAI_API_KEY=mock
MOCK_MODE=true
AI_MODEL=openai
ENVEOF
  echo "Edit .env with your Neon DATABASE_URL if needed."
else
  echo "[1/4] .env exists, using existing values."
fi

# Step 2: Start all services
echo "[2/4] Starting Redpanda + Backend + Dapr + Frontend..."
docker-compose up -d --build

# Step 3: Wait for health
echo "[3/4] Waiting for services to be healthy..."
until docker-compose exec -T backend curl -sf http://localhost:8000/health >/dev/null 2>&1; do
  echo "  Waiting for backend..."
  sleep 3
done
echo "  Backend healthy!"

# Step 4: Verify
echo "[4/4] Verifying services..."
echo ""
echo "Services:"
docker-compose ps
echo ""
echo "Redpanda topics:"
docker-compose exec -T redpanda rpk topic list 2>/dev/null || echo "  (topics created by redpanda-init)"
echo ""
echo "=== Ready ==="
echo ""
echo "Backend API:        http://localhost:8000"
echo "Backend docs:       http://localhost:8000/docs"
echo "Frontend:           http://localhost:3000"
echo "Redpanda Console:   http://localhost:8080"
echo ""
echo "Test commands:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost:8000/api/master/status"
echo "  curl http://localhost:8000/api/master/test-scenarios"
echo ""
echo "To stop: docker-compose down"
echo "To stop + clean: docker-compose down -v"
