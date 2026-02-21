# Task Operations — Add, Delete, Update, List

## API Endpoints (Backend)

| Action | Method | Endpoint | Body |
|--------|--------|----------|------|
| **List** | `GET` | `/api/tasks` | — |
| **Add** | `POST` | `/api/tasks` | `{ "description": "Buy milk" }` |
| **Update** | `PUT` | `/api/tasks/{id}` | `{ "description": "Buy milk and eggs" }` |
| **Delete** | `DELETE` | `/api/tasks/{id}` | — |
| **Toggle** | `PATCH` | `/api/tasks/{id}/toggle` | — |
| **Search** | `GET` | `/api/tasks/search?q=...&priority=...` | — |

All require `Authorization: Bearer <token>`.

---

## Frontend API Functions (`src/lib/api.ts`)

```typescript
import { getTasks, createTask, updateTask, deleteTask, toggleTask } from "@/lib/api";

// List all tasks
const { tasks, total } = await getTasks();

// Add task
const task = await createTask({ description: "Buy groceries" });

// Update task
await updateTask(1, { description: "Buy milk and eggs" });

// Delete task
await deleteTask(1);

// Toggle complete
await toggleTask(1);
```

---

## Dashboard Hooks (`src/hooks/useTasks.ts`)

```typescript
import { useTasks, useCreateTask, useUpdateTask, useDeleteTask, useToggleTask } from "@/hooks/useTasks";

const { tasks, refetch } = useTasks();
const { createTask } = useCreateTask();
const { updateTask } = useUpdateTask();
const { deleteTask } = useDeleteTask();
const { toggleTask } = useToggleTask();

// Add
await createTask({ description: "New task" });
refetch();

// Update
await updateTask(1, { description: "Updated" });
refetch();

// Delete
await deleteTask(1);
refetch();

// Toggle
await toggleTask(1);
refetch();
```

---

## Chat Commands (AI Chatbot)

| Action | Example |
|--------|---------|
| **List** | "Show my tasks", "List tasks", "What are my todos" |
| **Add** | "Add task buy groceries", "Create task call mom", "Remind me to submit report" |
| **Update** | "Update task 3 to buy milk", "Change task 2 to call dentist" |
| **Delete** | "Delete task 5", "Remove task 3" |
| **Complete** | "Complete task 1", "Mark task 2 as done" |

---

## cURL Examples

```bash
# Login first to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"YourPassword"}' \
  | jq -r '.access_token')

# List tasks
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks

# Add task
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"description":"Buy groceries"}' http://localhost:8000/api/tasks

# Update task 1
curl -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"description":"Buy milk and eggs"}' http://localhost:8000/api/tasks/1

# Delete task 1
curl -X DELETE -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks/1

# Toggle task 1
curl -X PATCH -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/tasks/1/toggle
```
