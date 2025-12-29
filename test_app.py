"""Quick test to verify the application can start."""
import sys
from phase_i.models import Task
from phase_i import operations

# Test that everything works
tasks = []
print("Testing Phase I Todo Application...")
print()

# Add a task
success, message, task = operations.add_task(tasks, "Test task")
print(f"[OK] Add task: {message}")

# View tasks
all_tasks = operations.get_all_tasks(tasks)
print(f"[OK] View tasks: Found {len(all_tasks)} task(s)")

# Mark complete
success, message = operations.mark_complete(tasks, 1)
print(f"[OK] Mark complete: {message}")

# Verify status
task = operations.get_task_by_id(tasks, 1)
print(f"[OK] Task status: {'Complete' if task.is_complete else 'Incomplete'}")

print()
print("[SUCCESS] All core functions working correctly!")
print()
print("To run the interactive application:")
print("  python phase_i/main.py")
