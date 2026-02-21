# AdvancedFeatureAgent — Reusable Intelligence (P+Q+P)

## Problem
Phase V requires advanced task management features beyond basic CRUD:
- Recurring tasks that auto-reschedule on completion
- Due dates with reminders via cron binding
- Priority levels (low/medium/high/urgent) for sorting
- User-defined tags for categorisation and search
- Full-text search, multi-field filtering, and flexible sorting

## Question
How do we implement all five features end-to-end across:
- Backend: SQLModel, FastAPI, Dapr, Kafka
- Frontend: Next.js, ChatKit, voice commands
- Agents: Mock provider NLP, tool definitions

## Pattern

### 1. Recurring Tasks
```
User creates task → recurring_pattern = "weekly"
User completes task → toggle endpoint
    ↓
emit_task_completed(recurring_pattern="weekly")
    ↓
event_service → Kafka "recurring-tasks" topic
    ↓
Dapr → /events/recurring-tasks
    ↓
RecurringTaskConsumer.process_event()
    ↓
Calculates next_due = current + 7 days
Creates new task (same desc, priority, tags, new due_date)
    ↓
Cycle repeats
```

### 2. Due Dates & Reminders
```
Task.due_date: datetime (indexed)
Task.reminder_at: datetime (cleared after firing)

Dapr cron binding → @every 5m
    ↓
POST /reminder-cron → process_due_reminders()
    ↓
SELECT WHERE reminder_at <= NOW() AND is_complete = FALSE
    ↓
emit_reminder() → Kafka "reminders" topic
    ↓
reminder_at = NULL (prevent duplicates)
```

### 3. Priorities
```
Levels: low → medium (default) → high → urgent
Model: Task.priority (varchar, indexed)
Schema: PriorityEnum validation
Route: /api/tasks/search?priority=high
Chat: "set task 5 priority to high" → update_todo
Display: Coloured badges (green/yellow/red/purple)
```

### 4. Tags
```
Storage: Task.tags = JSON string '["work","meeting"]'
Property: task.tags_list getter/setter
Create: POST /api/tasks {tags: ["work"]}
Search: /api/tasks/search?tag=work (ILIKE match)
Chat: "Add task deploy #devops" → extract_tags()
Display: Teal pills (#work, #devops)
```

### 5. Search / Filter / Sort
```
Endpoint: GET /api/tasks/search
  ?q=groceries          (keyword ILIKE)
  &priority=high        (exact match)
  &is_complete=false    (status filter)
  &tag=work             (tag ILIKE)
  &due_before=2026-03-01 (date range)
  &due_after=2026-02-01
  &sort_by=due_date     (created_at|updated_at|due_date|priority)
  &sort_order=asc       (asc|desc)

Overdue: GET /api/tasks/overdue
```

### Chat Commands (English + Urdu)
| Command | Feature |
|---------|---------|
| "Add urgent task deploy backend #devops" | priority + tags |
| "Set task 5 priority to high" | priority update |
| "Make task 3 repeat weekly" | recurring |
| "Search for urgent work tasks" | search + filter |
| "Show overdue tasks" | overdue detection |
| "Find tasks tagged #shopping" | tag search |
| "Show tasks due today" | due date filter |
| "Tag task 5 with work meeting" | tag update |
| "فوری ٹاسک شامل کریں" | Urdu priority |
| "مدت ختم شدہ ٹاسک دکھائیں" | Urdu overdue |

### Frontend Quick Commands (ChatInput)
The ChatInput component shows a scrollable row of quick-command buttons:
- My Tasks, Add Urgent, Overdue, Search, Due Today, #tagged
- Urdu equivalents when language = "ur"

### Reusability
1. Copy Task model fields + schemas to any SQLModel project
2. Copy search_tasks() service function for any entity search
3. Copy RecurringTaskConsumer for any recurring-pattern domain
4. The P+Q+P explanations serve as onboarding documentation
