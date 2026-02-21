# Phase II + Phase III Todo App - Complete Implementation

A complete, production-ready todo application implementing **all Phase II and Phase III requirements** from the specification documents.

## Live Demo (Vercel)

**Phase 5:** [https://phase5-todo-app.vercel.app](https://phase5-todo-app.vercel.app)

- Frontend deploy: [VERCEL_PHASE5_DEPLOY.md](VERCEL_PHASE5_DEPLOY.md)
- Backend deploy (Render): [BACKEND_DEPLOY.md](BACKEND_DEPLOY.md) — [Deploy to Render](https://render.com/deploy?repo=https://github.com/waqasvicky10/The-Evolution-Of-Todo-App)

---

## Phase IV Fallback: Docker Compose Deployment

If you encounter memory issues with Minikube/Hyper-V, use Docker Compose for local deployment. This simulates the Kubernetes environment using containers.

### Prerequisites
- Docker Desktop installed and running
- Docker Compose installed

### Setup & Run
1. **Copy Environment Variables**:
   ```powershell
   copy .env.example .env
   ```
   *Edit `.env` and add your `OPENAI_API_KEY` or leave `MOCK_MODE=true`.*

2. **Build and Start Services**:
   ```powershell
   docker-compose build
   docker-compose up -d
   ```

3. **Verify Deployment**:
   - **Backend API**: [http://localhost:8000/health](http://localhost:8000/health)
   - **Frontend App**: [http://localhost:3000](http://localhost:3000)

### Useful Commands
- **Stop Services**: `docker-compose down`
- **View Logs**: `docker-compose logs -f`
- **Rebuild**: `docker-compose up -d --build`

---


## Phase IV – Local Kubernetes Deployment

This phase focuses on deploying the Todo Chatbot monorepo to a local Kubernetes environment using Minikube and Helm.

### Prerequisites
- [Minikube](https://minikube.sigs.k8s.io/) (Run with Docker driver: `minikube start --driver=docker`)
- [Helm v3+](https://helm.sh/)
- `kubectl`
- AI Tools: `kubectl-ai`, `kagent`, `docker ai`

### Deployment Steps (PowerShell)

1. **Connect to Minikube Docker Daemon**
   ```powershell
   minikube docker-env | Invoke-Expression
   ```

2. **Build Container Images**
   ```powershell
   docker build -t todo-backend:latest -f docker/backend.Dockerfile .
   docker build -t todo-frontend:latest -f docker/frontend.Dockerfile .
   ```

3. **Configure Secrets**
   ```powershell
   # Use the provided template or manual command:
   kubectl create secret generic todo-secrets `
     --from-literal=database-url="sqlite:///./data/todo.db" `
     --from-literal=auth-secret="hackathon-secret-123" `
     --from-literal=openai-key="your-key-here"
   ```

4. **Install/Upgrade Charts**
   ```powershell
   helm upgrade --install backend ./charts/todo-backend
   helm upgrade --install frontend ./charts/todo-frontend
   ```

5. **Expose Services**
   ```powershell
   minikube service todo-frontend --url
   ```

### AI-Assisted Operations (Bonus)

- **Analyze Cluster Health**: `kagent analyze cluster health`
- **Scale Backend**: `kubectl-ai scale deployment backend to 3 replicas`
- **Debug Logs**: `kagent logs -f deployment/backend`

---

## ✅ Phase II Compliance

This app implements **all 10 User Stories** (US-201 to US-210) as specified in `PHASE_II_SPECIFICATION.md`:

### User Stories Implemented

1. **US-201: User Registration** ✅
   - Email and password registration
   - Password validation (8+ chars, uppercase, lowercase, number, special char)
   - Email format validation
   - Duplicate email prevention

2. **US-202: User Login** ✅
   - Secure authentication with bcrypt password hashing
   - JWT-like access tokens (15 minutes lifetime)
   - Refresh tokens (7 days lifetime)
   - Generic error messages for security

3. **US-203: User Logout** ✅
   - Secure logout with token invalidation
   - Session cleanup

4. **US-204: View Personal Task List** ✅
   - Display all user's tasks
   - Task count display
   - Empty state handling
   - User data isolation enforced

5. **US-205: Create a New Task** ✅
   - Task creation with validation (1-500 characters)
   - Automatic user association
   - Immediate feedback

6. **US-206: Update a Task** ✅
   - Edit task descriptions
   - Validation and error handling
   - User ownership verification

7. **US-207: Delete a Task** ✅
   - Secure task deletion
   - User ownership verification
   - Immediate removal from list

8. **US-208: Mark Task as Complete or Incomplete** ✅
   - Toggle completion status
   - Visual indicators (checkmarks, strikethrough)
   - User ownership verification

9. **US-209: Automatic Token Refresh** ✅
   - Automatic access token refresh using refresh token
   - Transparent token renewal
   - Session expiration handling

10. **US-210: Protected Route Access Control** ✅
    - Authentication required for dashboard
    - Automatic redirect to login for unauthenticated users
    - Token validation on all protected pages

## ✅ Phase III Compliance

This app implements **all Phase III conversational capabilities** as specified in `PHASE_III_SPECIFICATION.md`:

### Conversational Capabilities

1. **Add a Todo via Natural Language** ✅
   - Intent recognition for task creation
   - Natural language parsing
   - Conversational responses

2. **List Todos via Chat** ✅
   - View all tasks through chat
   - Formatted task lists
   - Empty state handling

3. **Update a Todo via Chat** ✅
   - Natural language task updates
   - Task reference resolution
   - Confirmation responses

4. **Mark a Todo as Complete via Chat** ✅
   - Complete tasks through conversation
   - Task identification
   - Encouraging responses

5. **Delete a Todo via Chat** ✅
   - Delete tasks via natural language
   - Task reference resolution
   - Confirmation messages

### Phase III Features

- ✅ **AI Chat Interface** - Conversational todo management
- ✅ **Natural Language Processing** - Intent recognition and understanding
- ✅ **Conversation History** - Persistent chat history storage
- ✅ **Contextual Responses** - Smart, conversational AI responses
- ✅ **Multi-Turn Conversations** - Context-aware conversations
- ✅ **Intent Recognition** - Keyword-based pattern matching
- ✅ **Conversation Persistence** - History across sessions

## 🎯 Dual Interface Mode

The app provides **two interfaces** that users can switch between:

### 1. Traditional UI (Phase II)
- Forms and buttons for task management
- Direct CRUD operations
- Visual task lists
- Inline editing

### 2. AI Chat Interface (Phase III)
- Natural language conversation
- Intent-based task management
- Conversational responses
- Chat history

**Users can seamlessly switch between both interfaces!**

## 🔒 Security Features

- ✅ **bcrypt password hashing** (Phase II requirement)
- ✅ **JWT-like token system** with expiration
- ✅ **User data isolation** - users can only access their own tasks
- ✅ **Token expiration enforcement** (15 min access, 7 day refresh)
- ✅ **Secure token storage** in database
- ✅ **Generic error messages** for security (no information leakage)

## 📋 Key Features

### Phase II Features
- User registration with strong password requirements
- Secure login with token-based authentication
- Task CRUD operations (Create, Read, Update, Delete)
- Mark tasks as complete/incomplete
- User data isolation (strict security)
- Automatic token refresh
- Comprehensive error handling
- Responsive design
- Empty state handling

### Phase III Features
- AI-powered chatbot interface
- Natural language task management
- Intent recognition (add, list, complete, delete, update)
- Conversation history storage
- Contextual AI responses
- Multi-turn conversations
- Seamless mode switching

## 🚀 Quick Start

### Local Development

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Streamlit Cloud Deployment

1. Push this repository to GitHub
2. Go to https://share.streamlit.io
3. Click "New app" or find your existing app
4. Select your repository
5. Set Main file path to: `streamlit_app.py`
6. Click "Deploy" or "Reboot app"

## 📖 Usage

### Traditional Interface
1. **Sign Up**: Create a new account
2. **Login**: Sign in with your credentials
3. **Manage Tasks**:
   - Click ➕ to add new tasks
   - Click ✅ to mark as complete
   - Click ↩️ to mark as incomplete
   - Click ✏️ to edit task description
   - Click 🗑️ to delete tasks

### AI Chat Interface
1. **Login**: Sign in to access the chat
2. **Switch to AI Chat**: Select "AI Chat" in the sidebar
3. **Chat with AI**:
   - **Add task**: "Add a task to buy groceries"
   - **List tasks**: "Show me all my tasks"
   - **Complete task**: "Mark the grocery task as done"
   - **Delete task**: "Delete the grocery task"
   - **Update task**: "Change the grocery task to buy vegetables"

### Example Chat Conversations

```
User: Add a task to buy groceries
AI: I've added 'buy groceries' to your todo list. ✅

User: Show me my tasks
AI: Here are your tasks:

Active Tasks (1):
1. buy groceries

User: Mark the grocery task as done
AI: Great! I've marked 'buy groceries' as complete. Well done! ✅
```

## 🔧 Technical Details

### Database Schema

- **users**: User accounts with bcrypt-hashed passwords
- **tasks**: User tasks with completion status
- **refresh_tokens**: Token management for session persistence
- **conversation_messages**: Chat history storage (Phase III)

### Token System

- **Access Token**: 15 minutes lifetime (JWT-like)
- **Refresh Token**: 7 days lifetime (stored in database)
- **Automatic Refresh**: Transparent token renewal

### Intent Recognition

The AI chatbot uses pattern-based intent recognition:
- **Create Intent**: "add", "create", "new", "remind me"
- **List Intent**: "show", "list", "display", "what"
- **Complete Intent**: "mark", "complete", "done", "finished"
- **Update Intent**: "change", "update", "modify", "edit"
- **Delete Intent**: "delete", "remove", "get rid of"

### Validation Rules

- **Email**: Valid email format, unique
- **Password**: 8+ chars, uppercase, lowercase, number, special char
- **Task Description**: 1-500 characters, non-empty

## 📚 Documentation

This implementation follows:
- `CONSTITUTION.md` - Project governance
- `PHASE_II_SPECIFICATION.md` - Phase II requirements
- `PHASE_II_PLAN.md` - Phase II implementation plan
- `PHASE_III_SPECIFICATION.md` - Phase III requirements
- `PHASE_III_PLAN.md` - Phase III implementation plan
- `PHASE_III_CONSTITUTION.md` - Phase III architectural principles

## ✅ Acceptance Criteria Met

### Phase II Acceptance Criteria
- ✅ Functional completeness (10 user stories)
- ✅ Security completeness (bcrypt, JWT, isolation)
- ✅ Error handling completeness
- ✅ Data persistence completeness
- ✅ User experience completeness

### Phase III Acceptance Criteria
- ✅ Conversational capabilities (5 core capabilities)
- ✅ Intent recognition and understanding
- ✅ Conversation history storage
- ✅ Multi-turn conversations
- ✅ Contextual responses
- ✅ Error handling for invalid commands
- ✅ Tool-based data operations (through existing Phase II functions)

## 📝 Requirements

- Python 3.8+
- Streamlit 1.28.0+
- bcrypt 4.0.0+

## 🎯 Project Status

**Status**: ✅ **COMPLETE**

- ✅ Phase II: All 10 user stories implemented
- ✅ Phase III: All conversational capabilities implemented
- ✅ Phase IV: Local Kubernetes deployment with Minikube
- ✅ Dual Interface: Traditional + AI Chat
- ✅ Production Ready: Fully tested and deployed

## 🌟 Highlights

- **Complete Phase II Implementation** - All 10 user stories with security
- **Complete Phase III Implementation** - AI chatbot with natural language
- **Dual Interface** - Traditional UI + AI Chat
- **Seamless Integration** - Both interfaces use the same database
- **Production Ready** - Error handling, validation, and security

## 🚀 Phase IV: Local Kubernetes Deployment with Minikube

Deploy the Todo App locally using Minikube and Helm charts.

### Prerequisites

- **Minikube** installed ([installation guide](https://minikube.sigs.k8s.io/docs/start/))
- **kubectl** installed ([installation guide](https://kubernetes.io/docs/tasks/tools/))
- **Helm 3** installed ([installation guide](https://helm.sh/docs/intro/install/))
- **Docker** installed and running

### 1. Start Minikube

```bash
# Start Minikube with recommended resources
minikube start --driver=docker --cpus=2 --memory=3072mb

# Verify Minikube is running
minikube status
```

### 2. Build Docker Images in Minikube

```bash
# Use Minikube's Docker daemon (important!)
# For PowerShell:
& minikube docker-env --shell powershell | Invoke-Expression

# For Bash/WSL:
eval $(minikube docker-env)

# Build backend image
docker build -f docker/backend.Dockerfile -t todo-backend:latest .

# Build frontend image
docker build -f docker/frontend.Dockerfile -t todo-frontend:latest .

# Verify images exist in Minikube
docker images | grep todo
```

### 3. Configure Secrets

```bash
# Copy the secrets template
cp k8s/secrets-template.yaml k8s/secrets.yaml

# Edit k8s/secrets.yaml with your values
# For base64 encoding in PowerShell:
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("your-value"))

# For base64 encoding in Bash/WSL:
echo -n "your-value" | base64

# Apply the secrets to Kubernetes
kubectl apply -f k8s/secrets.yaml
```

**Example Secrets:**
- `DATABASE_URL`: Your Neon PostgreSQL URL or `postgresql://user:pass@localhost/db`
- `BETTER_AUTH_SECRET`: Generate with `openssl rand -base64 32`
- `OPENAI_API_KEY`: Use `sk-dummy-mock-mode-key` for mock mode
- `MOCK_MODE`: Set to `"true"` to avoid API quota errors

### 4. Deploy with Helm

```bash
# Install backend service
helm install todo-backend charts/todo-backend/

# Install frontend service
helm install todo-frontend charts/todo-frontend/

# Check deployment status
kubectl get pods
kubectl get services

# Wait for pods to be ready (may take 1-2 minutes)
kubectl wait --for=condition=ready pod -l app=todo-backend --timeout=120s
kubectl wait --for=condition=ready pod -l app=todo-frontend --timeout=120s
```

### 5. Access the Application

```bash
# Get the frontend URL
minikube service todo-frontend --url

# Or access directly (NodePort 30080)
echo "http://$(minikube ip):30080"
```

Open the URL in your browser to access the Todo App!

### Troubleshooting

**Check Pod Logs:**
```bash
# Backend logs
kubectl logs -f deployment/todo-backend

# Frontend logs
kubectl logs -f deployment/todo-frontend
```

**Check Pod Status:**
```bash
# Describe pods for detailed error messages
kubectl describe pod -l app=todo-backend
kubectl describe pod -l app=todo-frontend

# Check all resources
kubectl get all
```

**Restart Deployments:**
```bash
# Restart backend
kubectl rollout restart deployment/todo-backend

# Restart frontend
kubectl rollout restart deployment/todo-frontend
```

**Rebuild and Redeploy:**
```bash
# Delete Helm releases
helm uninstall todo-backend
helm uninstall todo-frontend

# Rebuild images (make sure you're using Minikube's Docker daemon)
docker build -f docker/backend.Dockerfile -t todo-backend:latest .
docker build -f docker/frontend.Dockerfile -t todo-frontend:latest .

# Reinstall Helm charts
helm install todo-backend charts/todo-backend/
helm install todo-frontend charts/todo-frontend/
```

**Check Health Endpoints:**
```bash
# Port-forward backend to check health
kubectl port-forward deployment/todo-backend 8000:8000

# In another terminal or browser:
curl http://localhost:8000/health
```

**Common Issues:**

- **ImagePullBackOff**: Make sure images were built in Minikube's Docker daemon (`eval $(minikube docker-env)`)
- **CrashLoopBackOff**: Check logs with `kubectl logs` and verify secrets are correctly configured
- **Pods not starting**: Check resource limits - may need to increase Minikube memory
- **Cannot access frontend**: Verify NodePort service with `kubectl get svc` and use `minikube service todo-frontend`

### Cleanup

```bash
# Uninstall Helm releases
helm uninstall todo-backend
helm uninstall todo-frontend

# Delete secrets
kubectl delete secret todo-backend-secrets

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## 🤝 Contributing

This is a hackathon project demonstrating Phase II and Phase III of "The Evolution of Todo App". The implementation follows spec-driven development principles.

## 📝 License

This project is part of "The Evolution of Todo App" hackathon series.

---

**Built with ❤️ for The Evolution of Todo App Hackathon - Phases II, III & IV**
