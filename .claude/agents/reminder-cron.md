# Reminder Cron Agent — Reusable Intelligence (P+Q+P)

## Problem
Users set reminders on tasks (reminder_at field). The system must
check for due reminders periodically and publish notification events.

## Question
How do we implement a reliable cron job that:
- Runs every 5 minutes without manual scheduling?
- Processes all due reminders atomically?
- Clears processed reminders to avoid duplicates?
- Works both locally and in Kubernetes?

## Pattern

### Dapr Cron Binding
```yaml
# dapr/components/cron-binding.yaml
spec:
  type: bindings.cron
  metadata:
    - name: schedule
      value: "@every 5m"
    - name: direction
      value: "input"
```

### Handler
```
POST /reminder-cron  (invoked by Dapr)
  → reminder_service.process_due_reminders()
    → query tasks WHERE reminder_at <= NOW() AND is_complete = false
    → for each task:
        emit_reminder(task_id, user_id, description)
        set task.reminder_at = NULL  (prevent re-fire)
        commit
  → return {"processed": count}
```

### Reusability
1. Change the cron schedule in the YAML
2. Replace `process_due_reminders()` with your domain logic
3. The pattern works for any periodic job: cleanup, aggregation, sync
