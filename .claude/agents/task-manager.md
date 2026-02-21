# Task Manager Agent - Reusable Intelligence (P+Q+P)

## Problem
Users need to manage tasks through natural language via an AI chatbot.
The agent must understand intent (create, list, update, delete, search)
and execute the correct operation with user isolation.

## Question
How do we build a modular, reusable agent that:
- Parses natural language into structured task operations?
- Enforces user authentication and data isolation?
- Publishes events for every state change?
- Handles errors gracefully and responds in the user's language?

## Pattern

### Architecture
User -> ChatInput (voice/text) -> FastAPI /api/chat -> Agent Router
-> Skill Dispatcher (P+Q+P per skill)
-> AddTask / ListTasks / SearchTasks / UpdateTask / DeleteTask
-> TaskService -> DB (Neon PostgreSQL)
-> EventService -> Dapr PubSub -> Redpanda

### Skills (each follows P+Q+P)

- AddTask: Parse description, priority, tags, due_date from NL -> create_task()
- ListTasks: Parse filters -> get_user_tasks() or search_tasks()
- UpdateTask: Find task by ID/description -> update_task()
- DeleteTask: Find by ID/description -> delete_task()
- CompleteTask: Find by ID/description -> toggle_task()
- SearchTasks: Parse search params -> search_tasks()

### Reusability
- Each skill is a standalone module in backend/app/agents/
- Skills are registered in __init__.py for auto-discovery
- Event emissions are decoupled (fire-and-forget via BackgroundTasks)
- Translation is handled at the response layer (not in business logic)
- Mock provider enables zero-cost development and testing

### Transfer Pattern
To reuse this agent in another project:
1. Copy backend/app/agents/ folder
2. Copy backend/app/services/event_service.py
3. Adjust model imports to match your domain
4. Register skills in your FastAPI router
5. Provide Dapr component YAMLs for your infrastructure
