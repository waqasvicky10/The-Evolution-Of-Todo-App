# PHASE I IMPLEMENTATION TASKS

**Project:** Evolution of Todo
**Phase:** I - Foundation
**Version:** 1.0
**Status:** APPROVED
**Parent Documents:**
- CONSTITUTION.md
- PHASE_I_SPECIFICATION.md
- PHASE_I_PLAN.md
**Date:** 2025-12-29

---

## EXECUTIVE SUMMARY

This document breaks down the Phase I technical plan into atomic, sequential implementation tasks. Each task is independently implementable, testable, and verifiable against the specification.

---

## CONSTITUTIONAL COMPLIANCE

This task breakdown is created under:
- **Article I, Section 1.4:** Task Requirements
- **Article II, Section 2.2:** Strict Specification Adherence
- **Constitutional Workflow:** Constitution → Spec → Plan → **Tasks** → Code

All tasks implement ONLY what is specified in PHASE_I_SPECIFICATION.md and PHASE_I_PLAN.md.

---

## TASK STRUCTURE

Each task includes:
- **Task ID:** Unique identifier (TASK-001, TASK-002, etc.)
- **Title:** Clear, action-oriented description
- **Description:** What needs to be implemented
- **Preconditions:** What must exist before starting
- **Specification References:** Relevant spec sections
- **Plan References:** Relevant plan sections
- **Artifacts:** Files to create or modify
- **Acceptance Criteria:** How to verify completion
- **Estimated Complexity:** Small/Medium (all are small or medium)
- **Dependencies:** Which tasks must complete first

---

## TASK DEPENDENCY GRAPH

```
TASK-001 (Project Structure)
    ↓
TASK-002 (Task Model) → TASK-003 (Model Tests)
    ↓                         ↓
TASK-004 (ID Generation) → TASK-005 (Add Task Op) → TASK-006 (Operations Tests Part 1)
    ↓                                                       ↓
TASK-007 (Get Operations) ────────────────────────────────┘
    ↓
TASK-008 (Update/Delete Ops) → TASK-009 (Operations Tests Part 2)
    ↓                                ↓
TASK-010 (Mark Complete/Incomplete) → TASK-011 (Operations Tests Part 3)
    ↓                                       ↓
TASK-012 (Display Functions) ──────────────┘
    ↓
TASK-013 (Input Functions) → TASK-014 (UI Tests)
    ↓                              ↓
TASK-015 (Main Entry Point) ──────┘
    ↓
TASK-016 (Menu Loop) → TASK-017 (Handler Functions)
    ↓                        ↓
TASK-018 (Exception Handling) ─┘
    ↓
TASK-019 (Integration Tests)
    ↓
TASK-020 (Quality Assurance)
    ↓
TASK-021 (Manual Testing & Documentation)
    ↓
[PHASE I COMPLETE]
```

---

## TASK DETAILS

---

### TASK-001: Create Project Structure

**Title:** Set up Phase I project structure and initialize Python package

**Description:**
Create the directory structure for Phase I implementation including main package directory, test directory, and necessary `__init__.py` files.

**Preconditions:**
- CONSTITUTION.md exists
- PHASE_I_SPECIFICATION.md exists
- PHASE_I_PLAN.md exists
- Working directory is E:\heckathon-2

**Specification References:**
- PHASE_I_SPECIFICATION.md: "Technology Requirements" section

**Plan References:**
- PHASE_I_PLAN.md: Section 8.5 "Project Structure (Final)"

**Artifacts to Create:**
```
phase_i/__init__.py           (empty file)
tests/phase_i/__init__.py     (empty file)
```

**Artifacts to Verify Exist:**
```
heckathon-2/
├── CONSTITUTION.md
├── PHASE_I_SPECIFICATION.md
├── PHASE_I_PLAN.md
├── phase_i/
│   └── __init__.py
└── tests/
    └── phase_i/
        └── __init__.py
```

**Acceptance Criteria:**
- [ ] `phase_i/` directory exists
- [ ] `phase_i/__init__.py` exists (can be empty)
- [ ] `tests/phase_i/` directory exists
- [ ] `tests/phase_i/__init__.py` exists (can be empty)
- [ ] Python can import the package: `python -c "import phase_i"`

**Estimated Complexity:** Small

**Dependencies:** None

---

### TASK-002: Implement Task Data Model

**Title:** Create Task entity with dataclass and validation

**Description:**
Implement the Task data model as a Python dataclass with fields `id`, `description`, and `is_complete`. Include field validation and a helper function to validate task descriptions.

**Preconditions:**
- TASK-001 complete
- `phase_i/__init__.py` exists

**Specification References:**
- PHASE_I_SPECIFICATION.md: "Data Model" section
- Task entity definition with constraints

**Plan References:**
- PHASE_I_PLAN.md: Section 2.2 "Task Entity Definition"
- PHASE_I_PLAN.md: Section 5.1 "Layer 1: Domain Model (models.py)"

**Artifacts to Create:**
```
phase_i/models.py
```

**Implementation Requirements:**

```python
from dataclasses import dataclass

@dataclass
class Task:
    """
    Represents a single todo task.

    Attributes:
        id: Unique positive integer identifier
        description: Task description (1-500 characters)
        is_complete: Task completion status (default False)
    """
    id: int
    description: str
    is_complete: bool = False

    def __post_init__(self) -> None:
        """Validate task fields after initialization."""
        if self.id < 1:
            raise ValueError("Task ID must be positive")
        if not self.description or len(self.description) > 500:
            raise ValueError("Description must be 1-500 characters")


def validate_description(description: str) -> bool:
    """
    Validate task description meets constraints.

    Args:
        description: Task description to validate

    Returns:
        True if valid, False otherwise
    """
    if not description:
        return False
    if len(description) > 500:
        return False
    return True
```

**Acceptance Criteria:**
- [ ] `phase_i/models.py` exists
- [ ] Task dataclass defined with fields: id, description, is_complete
- [ ] is_complete defaults to False
- [ ] `__post_init__` validates id > 0
- [ ] `__post_init__` validates description length (1-500)
- [ ] `validate_description()` function implemented
- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] Can create valid Task: `Task(1, "Buy groceries")`
- [ ] Invalid Task raises ValueError

**Estimated Complexity:** Small

**Dependencies:** TASK-001

---

### TASK-003: Write Unit Tests for Task Model

**Title:** Create comprehensive unit tests for models.py

**Description:**
Write unit tests covering Task creation, validation, default values, and error cases.

**Preconditions:**
- TASK-002 complete
- `phase_i/models.py` exists with Task and validate_description

**Specification References:**
- PHASE_I_SPECIFICATION.md: "Testing Requirements" section
- Minimum 80% coverage requirement

**Plan References:**
- PHASE_I_PLAN.md: Section 7.2 "Testing Strategy" - test_models.py

**Artifacts to Create:**
```
tests/phase_i/test_models.py
```

**Test Cases to Implement:**
1. `test_task_creation_valid()` - Create task with valid data
2. `test_task_creation_with_defaults()` - Verify is_complete defaults to False
3. `test_task_invalid_id_zero()` - Task with id=0 raises ValueError
4. `test_task_invalid_id_negative()` - Task with id=-1 raises ValueError
5. `test_task_empty_description()` - Empty description raises ValueError
6. `test_task_description_too_long()` - 501 char description raises ValueError
7. `test_task_description_exactly_500()` - 500 char description is valid
8. `test_validate_description_valid()` - Returns True for valid description
9. `test_validate_description_empty()` - Returns False for empty string
10. `test_validate_description_too_long()` - Returns False for 501 chars
11. `test_task_is_complete_true()` - Can create completed task

**Implementation Requirements:**
```python
import pytest
from phase_i.models import Task, validate_description


def test_task_creation_valid():
    """Test creating a task with valid data."""
    task = Task(id=1, description="Buy groceries")
    assert task.id == 1
    assert task.description == "Buy groceries"
    assert task.is_complete is False


def test_task_invalid_id_zero():
    """Test that id=0 raises ValueError."""
    with pytest.raises(ValueError, match="Task ID must be positive"):
        Task(id=0, description="Test")

# ... etc
```

**Acceptance Criteria:**
- [ ] `tests/phase_i/test_models.py` exists
- [ ] All 11 test cases implemented
- [ ] All tests pass: `pytest tests/phase_i/test_models.py`
- [ ] Coverage ≥95% for models.py: `pytest --cov=phase_i.models`
- [ ] Tests use pytest framework
- [ ] Tests have descriptive names and docstrings

**Estimated Complexity:** Small

**Dependencies:** TASK-002

---

### TASK-004: Implement ID Generation

**Title:** Create get_next_id function in operations.py

**Description:**
Implement the ID generation algorithm that returns the next sequential task ID based on the current task list.

**Preconditions:**
- TASK-002 complete
- `phase_i/models.py` exists

**Specification References:**
- PHASE_I_SPECIFICATION.md: "Data Model" section - ID constraints

**Plan References:**
- PHASE_I_PLAN.md: Section 3 "Task Identification Strategy"
- PHASE_I_PLAN.md: Section 3.1 "ID Generation Algorithm"

**Artifacts to Create:**
```
phase_i/operations.py
```

**Implementation Requirements:**

```python
from typing import List
from phase_i.models import Task


def get_next_id(tasks: List[Task]) -> int:
    """
    Generate next available task ID.

    Args:
        tasks: Current list of tasks

    Returns:
        Next sequential ID (1 if list empty, max_id + 1 otherwise)
    """
    if not tasks:
        return 1
    return max(task.id for task in tasks) + 1
```

**Acceptance Criteria:**
- [ ] `phase_i/operations.py` exists
- [ ] `get_next_id()` function implemented
- [ ] Returns 1 for empty list
- [ ] Returns max(id) + 1 for non-empty list
- [ ] Handles gaps in IDs correctly (e.g., [1, 3, 5] → 6)
- [ ] Function has type hints
- [ ] Function has docstring
- [ ] Can be imported: `from phase_i.operations import get_next_id`

**Estimated Complexity:** Small

**Dependencies:** TASK-002

---

### TASK-005: Implement Add Task Operation

**Title:** Create add_task function in operations.py

**Description:**
Implement the add_task function that creates a new task with the next available ID and adds it to the task list.

**Preconditions:**
- TASK-004 complete
- `phase_i/operations.py` exists with get_next_id

**Specification References:**
- PHASE_I_SPECIFICATION.md: "User Stories" - US-101: Add Task
- Acceptance criteria and error cases

**Plan References:**
- PHASE_I_PLAN.md: Section 5.2 "Layer 2: Business Logic (operations.py)"
- add_task function signature and implementation

**Artifacts to Modify:**
```
phase_i/operations.py
```

**Implementation Requirements:**

```python
from typing import List, Tuple, Optional
from phase_i.models import Task, validate_description


def add_task(tasks: List[Task], description: str) -> Tuple[bool, str, Optional[Task]]:
    """
    Add new task to list.

    Args:
        tasks: Task list (modified in-place)
        description: Task description

    Returns:
        Tuple of (success, message, created_task)
        - (True, success_message, task) on success
        - (False, error_message, None) on failure
    """
    # Validate description
    if not description.strip():
        return (False, "Task description cannot be empty", None)

    if len(description) > 500:
        return (False, "Task description too long (max 500 characters)", None)

    # Generate ID and create task
    next_id = get_next_id(tasks)
    new_task = Task(id=next_id, description=description.strip(), is_complete=False)
    tasks.append(new_task)

    return (True, f'Task added with ID {next_id}: "{description.strip()}"', new_task)
```

**Acceptance Criteria:**
- [ ] `add_task()` function implemented in operations.py
- [ ] Returns (True, message, task) on success
- [ ] Returns (False, error_message, None) for empty description
- [ ] Returns (False, error_message, None) for >500 char description
- [ ] Strips whitespace from description
- [ ] Task appended to list on success
- [ ] Generated ID is sequential
- [ ] Function has type hints
- [ ] Function has docstring

**Estimated Complexity:** Small

**Dependencies:** TASK-004

---

### TASK-006: Write Unit Tests for ID Generation and Add Task

**Title:** Create unit tests for get_next_id and add_task

**Description:**
Write comprehensive unit tests for the ID generation and add task operations.

**Preconditions:**
- TASK-005 complete
- `phase_i/operations.py` has get_next_id and add_task

**Specification References:**
- PHASE_I_SPECIFICATION.md: "Testing Requirements"
- US-101 acceptance criteria

**Plan References:**
- PHASE_I_PLAN.md: Section 7.2 "Testing Strategy" - test_operations.py

**Artifacts to Create:**
```
tests/phase_i/test_operations.py
```

**Test Cases to Implement:**

**get_next_id tests:**
1. `test_get_next_id_empty_list()` - Returns 1 for empty list
2. `test_get_next_id_single_task()` - Returns 2 when list has task with id=1
3. `test_get_next_id_multiple_tasks()` - Returns max+1 for multiple tasks
4. `test_get_next_id_with_gaps()` - Handles gaps correctly (e.g., [1, 3] → 4)

**add_task tests:**
5. `test_add_task_valid()` - Successfully adds task with valid description
6. `test_add_task_empty_description()` - Returns error for empty string
7. `test_add_task_whitespace_only()` - Returns error for whitespace-only
8. `test_add_task_description_too_long()` - Returns error for 501 chars
9. `test_add_task_description_exactly_500()` - Succeeds with 500 chars
10. `test_add_task_strips_whitespace()` - Strips leading/trailing whitespace
11. `test_add_task_multiple_tasks()` - IDs increment correctly
12. `test_add_task_returns_created_task()` - Returns created task object

**Acceptance Criteria:**
- [ ] `tests/phase_i/test_operations.py` exists
- [ ] All 12 test cases implemented
- [ ] All tests pass: `pytest tests/phase_i/test_operations.py`
- [ ] Tests verify return tuple structure
- [ ] Tests verify list modification (in-place)
- [ ] Tests verify error messages match specification
- [ ] Coverage includes success and error paths

**Estimated Complexity:** Small

**Dependencies:** TASK-005

---

### TASK-007: Implement Get Operations

**Title:** Create get_all_tasks and get_task_by_id functions

**Description:**
Implement functions to retrieve all tasks and find a specific task by ID.

**Preconditions:**
- TASK-005 complete
- `phase_i/operations.py` exists

**Specification References:**
- PHASE_I_SPECIFICATION.md: US-102 (View Task List)
- US-103, US-104, US-105, US-106 (require finding tasks by ID)

**Plan References:**
- PHASE_I_PLAN.md: Section 5.2 "Layer 2: Business Logic"
- get_all_tasks and get_task_by_id function signatures

**Artifacts to Modify:**
```
phase_i/operations.py
```

**Implementation Requirements:**

```python
def get_all_tasks(tasks: List[Task]) -> List[Task]:
    """
    Get all tasks.

    Args:
        tasks: Task list

    Returns:
        List of all tasks (same reference, not a copy)
    """
    return tasks


def get_task_by_id(tasks: List[Task], task_id: int) -> Optional[Task]:
    """
    Find task by ID.

    Args:
        tasks: Task list
        task_id: ID to search for

    Returns:
        Task if found, None otherwise
    """
    return next((task for task in tasks if task.id == task_id), None)
```

**Acceptance Criteria:**
- [ ] `get_all_tasks()` implemented - returns task list
- [ ] `get_task_by_id()` implemented - finds task by ID
- [ ] get_task_by_id returns None if not found
- [ ] get_task_by_id returns Task object if found
- [ ] Functions have type hints
- [ ] Functions have docstrings
- [ ] Can be imported successfully

**Estimated Complexity:** Small

**Dependencies:** TASK-005

---

### TASK-008: Implement Update and Delete Operations

**Title:** Create update_task and delete_task functions

**Description:**
Implement functions to update a task's description and delete a task from the list.

**Preconditions:**
- TASK-007 complete
- get_task_by_id function exists

**Specification References:**
- PHASE_I_SPECIFICATION.md: US-103 (Update Task)
- PHASE_I_SPECIFICATION.md: US-104 (Delete Task)
- Acceptance criteria and error cases

**Plan References:**
- PHASE_I_PLAN.md: Section 5.2 "Layer 2: Business Logic"
- update_task and delete_task function signatures

**Artifacts to Modify:**
```
phase_i/operations.py
```

**Implementation Requirements:**

```python
def update_task(tasks: List[Task], task_id: int, new_description: str) -> Tuple[bool, str]:
    """
    Update task description.

    Args:
        tasks: Task list
        task_id: ID of task to update
        new_description: New description text

    Returns:
        Tuple of (success, message)
    """
    task = get_task_by_id(tasks, task_id)
    if not task:
        return (False, f"Task with ID {task_id} not found")

    if not new_description.strip():
        return (False, "Task description cannot be empty")

    if len(new_description) > 500:
        return (False, "Task description too long (max 500 characters)")

    task.description = new_description.strip()
    return (True, f'Task {task_id} updated to "{new_description.strip()}"')


def delete_task(tasks: List[Task], task_id: int) -> Tuple[bool, str]:
    """
    Delete task from list.

    Args:
        tasks: Task list (modified in-place)
        task_id: ID of task to delete

    Returns:
        Tuple of (success, message)
    """
    task = get_task_by_id(tasks, task_id)
    if not task:
        return (False, f"Task with ID {task_id} not found")

    tasks.remove(task)
    return (True, f"Task {task_id} deleted")
```

**Acceptance Criteria:**
- [ ] `update_task()` implemented
- [ ] update_task validates task exists
- [ ] update_task validates new description (not empty, ≤500 chars)
- [ ] update_task modifies task in-place
- [ ] update_task strips whitespace
- [ ] `delete_task()` implemented
- [ ] delete_task validates task exists
- [ ] delete_task removes task from list
- [ ] Functions return (bool, str) tuples
- [ ] Functions have type hints and docstrings

**Estimated Complexity:** Small

**Dependencies:** TASK-007

---

### TASK-009: Write Unit Tests for Update and Delete Operations

**Title:** Create unit tests for update_task and delete_task

**Description:**
Write comprehensive unit tests for update and delete operations.

**Preconditions:**
- TASK-008 complete
- update_task and delete_task functions exist

**Specification References:**
- PHASE_I_SPECIFICATION.md: US-103, US-104 acceptance criteria

**Plan References:**
- PHASE_I_PLAN.md: Section 7.2 "Testing Strategy"

**Artifacts to Modify:**
```
tests/phase_i/test_operations.py
```

**Test Cases to Add:**

**get_all_tasks tests:**
1. `test_get_all_tasks_empty()` - Returns empty list
2. `test_get_all_tasks_multiple()` - Returns all tasks

**get_task_by_id tests:**
3. `test_get_task_by_id_found()` - Returns task when exists
4. `test_get_task_by_id_not_found()` - Returns None when not exists
5. `test_get_task_by_id_empty_list()` - Returns None for empty list

**update_task tests:**
6. `test_update_task_valid()` - Successfully updates description
7. `test_update_task_not_found()` - Returns error for invalid ID
8. `test_update_task_empty_description()` - Returns error for empty string
9. `test_update_task_too_long()` - Returns error for 501 chars
10. `test_update_task_strips_whitespace()` - Strips whitespace

**delete_task tests:**
11. `test_delete_task_valid()` - Successfully removes task
12. `test_delete_task_not_found()` - Returns error for invalid ID
13. `test_delete_task_list_modified()` - Verifies list length decreases

**Acceptance Criteria:**
- [ ] All 13 new test cases added to test_operations.py
- [ ] All tests pass
- [ ] Tests verify tuple return structures
- [ ] Tests verify error messages match specification
- [ ] Coverage ≥80% for operations.py

**Estimated Complexity:** Small

**Dependencies:** TASK-008

---

### TASK-010: Implement Mark Complete/Incomplete Operations

**Title:** Create mark_complete and mark_incomplete functions

**Description:**
Implement functions to mark tasks as complete or incomplete.

**Preconditions:**
- TASK-007 complete
- get_task_by_id function exists

**Specification References:**
- PHASE_I_SPECIFICATION.md: US-105 (Mark Task Complete)
- PHASE_I_SPECIFICATION.md: US-106 (Mark Task Incomplete)

**Plan References:**
- PHASE_I_PLAN.md: Section 5.2 "Layer 2: Business Logic"

**Artifacts to Modify:**
```
phase_i/operations.py
```

**Implementation Requirements:**

```python
def mark_complete(tasks: List[Task], task_id: int) -> Tuple[bool, str]:
    """
    Mark task as complete.

    Args:
        tasks: Task list
        task_id: ID of task to mark complete

    Returns:
        Tuple of (success, message)
    """
    task = get_task_by_id(tasks, task_id)
    if not task:
        return (False, f"Task with ID {task_id} not found")

    if task.is_complete:
        return (True, f"Info: Task {task_id} is already marked complete")

    task.is_complete = True
    return (True, f"Task {task_id} marked as complete")


def mark_incomplete(tasks: List[Task], task_id: int) -> Tuple[bool, str]:
    """
    Mark task as incomplete.

    Args:
        tasks: Task list
        task_id: ID of task to mark incomplete

    Returns:
        Tuple of (success, message)
    """
    task = get_task_by_id(tasks, task_id)
    if not task:
        return (False, f"Task with ID {task_id} not found")

    if not task.is_complete:
        return (True, f"Info: Task {task_id} is already marked incomplete")

    task.is_complete = False
    return (True, f"Task {task_id} marked as incomplete")
```

**Acceptance Criteria:**
- [ ] `mark_complete()` implemented
- [ ] mark_complete validates task exists
- [ ] mark_complete handles already-complete case (informational message)
- [ ] mark_complete sets is_complete to True
- [ ] `mark_incomplete()` implemented
- [ ] mark_incomplete validates task exists
- [ ] mark_incomplete handles already-incomplete case (informational message)
- [ ] mark_incomplete sets is_complete to False
- [ ] Functions return (bool, str) tuples
- [ ] Functions have type hints and docstrings

**Estimated Complexity:** Small

**Dependencies:** TASK-007

---

### TASK-011: Write Unit Tests for Mark Complete/Incomplete

**Title:** Create unit tests for mark_complete and mark_incomplete

**Description:**
Write comprehensive unit tests for mark complete and incomplete operations.

**Preconditions:**
- TASK-010 complete
- mark_complete and mark_incomplete functions exist

**Specification References:**
- PHASE_I_SPECIFICATION.md: US-105, US-106 acceptance criteria

**Plan References:**
- PHASE_I_PLAN.md: Section 7.2 "Testing Strategy"

**Artifacts to Modify:**
```
tests/phase_i/test_operations.py
```

**Test Cases to Add:**

**mark_complete tests:**
1. `test_mark_complete_valid()` - Successfully marks incomplete task complete
2. `test_mark_complete_not_found()` - Returns error for invalid ID
3. `test_mark_complete_already_complete()` - Returns info message
4. `test_mark_complete_status_changed()` - Verifies is_complete = True

**mark_incomplete tests:**
5. `test_mark_incomplete_valid()` - Successfully marks complete task incomplete
6. `test_mark_incomplete_not_found()` - Returns error for invalid ID
7. `test_mark_incomplete_already_incomplete()` - Returns info message
8. `test_mark_incomplete_status_changed()` - Verifies is_complete = False

**Acceptance Criteria:**
- [ ] All 8 new test cases added to test_operations.py
- [ ] All tests pass
- [ ] Tests verify status changes correctly
- [ ] Tests verify informational messages for already-completed/incomplete
- [ ] Coverage maintained at ≥80% for operations.py
- [ ] All operations.py functions now tested

**Estimated Complexity:** Small

**Dependencies:** TASK-010

---

### TASK-012: Implement Display Functions

**Title:** Create display functions in ui.py

**Description:**
Implement all display/output functions for the CLI including welcome screen, menu, task list display, and error/success messages.

**Preconditions:**
- TASK-010 complete (all operations exist)
- operations.py fully implemented

**Specification References:**
- PHASE_I_SPECIFICATION.md: "CLI Interaction Flow" section
- Display format examples for all screens

**Plan References:**
- PHASE_I_PLAN.md: Section 5.3 "Layer 3: Presentation (ui.py)"
- PHASE_I_PLAN.md: Section 4 "CLI Control Flow"

**Artifacts to Create:**
```
phase_i/ui.py
```

**Implementation Requirements:**

```python
from typing import List
from phase_i.models import Task


def display_welcome() -> None:
    """Display welcome screen."""
    print("\n" + "=" * 40)
    print("    WELCOME TO TODO LIST MANAGER")
    print("=" * 40)


def display_menu() -> None:
    """Display main menu."""
    print("\n" + "=" * 40)
    print("           MAIN MENU")
    print("=" * 40)
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task Complete")
    print("6. Mark Task Incomplete")
    print("7. Exit")
    print("=" * 40)


def display_tasks(tasks: List[Task]) -> None:
    """
    Display formatted task list.

    Args:
        tasks: List of tasks to display
    """
    if not tasks:
        print("\nNo tasks found. Add a task to get started.")
        return

    print(f"\nYour Tasks ({len(tasks)} total):")
    print("-" * 40)
    for task in tasks:
        status = "✓" if task.is_complete else "✗"
        print(f"ID: {task.id} | Status: {status} | {task.description}")
    print("-" * 40)


def display_error(message: str) -> None:
    """
    Display error message.

    Args:
        message: Error message to display
    """
    print(f"\nError: {message}")


def display_success(message: str) -> None:
    """
    Display success message.

    Args:
        message: Success message to display
    """
    print(f"\nSuccess: {message}")


def display_goodbye() -> None:
    """Display goodbye message."""
    print("\n" + "=" * 40)
    print("Thank you for using Todo List Manager!")
    print("Goodbye!")
    print("=" * 40)


def pause() -> None:
    """Wait for user to press Enter."""
    input("\nPress Enter to continue...")
```

**Acceptance Criteria:**
- [ ] `phase_i/ui.py` exists
- [ ] `display_welcome()` implemented - shows welcome banner
- [ ] `display_menu()` implemented - shows 7 menu options
- [ ] `display_tasks()` implemented - formats task list per spec
- [ ] display_tasks handles empty list with appropriate message
- [ ] display_tasks shows ID, status (✓/✗), description
- [ ] `display_error()` implemented - formats error messages
- [ ] `display_success()` implemented - formats success messages
- [ ] `display_goodbye()` implemented - shows goodbye banner
- [ ] `pause()` implemented - waits for Enter key
- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] Output format matches specification examples

**Estimated Complexity:** Small

**Dependencies:** TASK-010

---

### TASK-013: Implement Input Functions

**Title:** Create input validation functions in ui.py

**Description:**
Implement all input capture and validation functions including menu choice, task ID, task description, and confirmation prompts.

**Preconditions:**
- TASK-012 complete
- ui.py exists with display functions

**Specification References:**
- PHASE_I_SPECIFICATION.md: "CLI Interaction Flow"
- PHASE_I_SPECIFICATION.md: "Error Handling" section

**Plan References:**
- PHASE_I_PLAN.md: Section 4.3 "Input Handling Strategy"
- PHASE_I_PLAN.md: Section 5.3 "Layer 3: Presentation (ui.py)"

**Artifacts to Modify:**
```
phase_i/ui.py
```

**Implementation Requirements:**

```python
def get_menu_choice() -> int:
    """
    Prompt user for menu choice and validate.

    Returns:
        Valid menu choice (1-7)
    """
    while True:
        user_input = input("Enter your choice (1-7): ").strip()

        try:
            choice = int(user_input)
            if 1 <= choice <= 7:
                return choice
            else:
                display_error("Invalid choice. Please enter a number between 1 and 7.")
        except ValueError:
            display_error("Invalid choice. Please enter a number between 1 and 7.")


def get_task_id() -> int:
    """
    Prompt user for task ID and validate format.

    Returns:
        Integer task ID (existence checked elsewhere)
    """
    while True:
        user_input = input("Enter task ID: ").strip()

        try:
            task_id = int(user_input)
            return task_id
        except ValueError:
            display_error("Task ID must be a number")


def get_task_description() -> str:
    """
    Prompt user for task description and validate.

    Returns:
        Valid task description (1-500 chars)
    """
    while True:
        description = input("Enter task description: ").strip()

        if not description:
            display_error("Task description cannot be empty")
        elif len(description) > 500:
            display_error("Task description too long (max 500 characters)")
        else:
            return description


def get_confirmation() -> bool:
    """
    Prompt user for Y/N confirmation.

    Returns:
        True if confirmed (Y/Yes), False if declined (N/No)
    """
    while True:
        user_input = input("Are you sure you want to delete this task? (Y/N): ").strip().upper()

        if user_input in ['Y', 'YES']:
            return True
        elif user_input in ['N', 'NO']:
            return False
        else:
            display_error("Please enter Y or N")
```

**Acceptance Criteria:**
- [ ] `get_menu_choice()` implemented
- [ ] get_menu_choice loops until valid input (1-7)
- [ ] get_menu_choice shows error for non-numeric input
- [ ] get_menu_choice shows error for out-of-range input
- [ ] `get_task_id()` implemented
- [ ] get_task_id loops until valid integer
- [ ] get_task_id shows error for non-numeric input
- [ ] `get_task_description()` implemented
- [ ] get_task_description validates not empty
- [ ] get_task_description validates ≤500 characters
- [ ] get_task_description strips whitespace
- [ ] `get_confirmation()` implemented
- [ ] get_confirmation accepts Y/N (case-insensitive)
- [ ] get_confirmation loops until valid input
- [ ] All functions have type hints and docstrings
- [ ] All validation loops use display_error()

**Estimated Complexity:** Small

**Dependencies:** TASK-012

---

### TASK-014: Write Unit Tests for UI Functions

**Title:** Create unit tests for ui.py

**Description:**
Write unit tests for display and input functions using stdout/stdin mocking.

**Preconditions:**
- TASK-013 complete
- ui.py fully implemented

**Specification References:**
- PHASE_I_SPECIFICATION.md: "Testing Requirements"

**Plan References:**
- PHASE_I_PLAN.md: Section 7.2 "Testing Strategy" - test_ui.py

**Artifacts to Create:**
```
tests/phase_i/test_ui.py
```

**Test Cases to Implement:**

**Display function tests (capture stdout):**
1. `test_display_welcome()` - Verifies welcome banner output
2. `test_display_menu()` - Verifies menu options 1-7
3. `test_display_tasks_empty()` - Shows "No tasks found" message
4. `test_display_tasks_single()` - Formats single task correctly
5. `test_display_tasks_multiple()` - Formats multiple tasks
6. `test_display_tasks_complete_status()` - Shows ✓ for complete tasks
7. `test_display_tasks_incomplete_status()` - Shows ✗ for incomplete tasks
8. `test_display_error()` - Formats error with "Error:" prefix
9. `test_display_success()` - Formats success with "Success:" prefix
10. `test_display_goodbye()` - Shows goodbye banner

**Input function tests (mock stdin):**
11. `test_get_menu_choice_valid()` - Returns valid choice
12. `test_get_menu_choice_invalid_then_valid()` - Loops on error
13. `test_get_task_id_valid()` - Returns integer ID
14. `test_get_task_id_invalid_then_valid()` - Loops on non-numeric
15. `test_get_task_description_valid()` - Returns trimmed description
16. `test_get_task_description_empty_then_valid()` - Loops on empty
17. `test_get_confirmation_yes()` - Returns True for 'Y'
18. `test_get_confirmation_no()` - Returns False for 'N'
19. `test_get_confirmation_case_insensitive()` - Accepts 'y', 'YES', etc.

**Implementation Notes:**
```python
import pytest
from unittest.mock import patch
from io import StringIO
from phase_i.ui import display_tasks, get_menu_choice
from phase_i.models import Task


def test_display_tasks_multiple(capsys):
    """Test displaying multiple tasks."""
    tasks = [
        Task(1, "Buy groceries", False),
        Task(2, "Finish homework", True)
    ]
    display_tasks(tasks)
    captured = capsys.readouterr()
    assert "Your Tasks (2 total)" in captured.out
    assert "ID: 1 | Status: ✗ | Buy groceries" in captured.out
    assert "ID: 2 | Status: ✓ | Finish homework" in captured.out


@patch('builtins.input', side_effect=['3'])
def test_get_menu_choice_valid(mock_input):
    """Test getting valid menu choice."""
    choice = get_menu_choice()
    assert choice == 3
```

**Acceptance Criteria:**
- [ ] `tests/phase_i/test_ui.py` exists
- [ ] All 19 test cases implemented
- [ ] Display tests use capsys fixture to capture output
- [ ] Input tests use mock.patch to simulate user input
- [ ] Input validation loop tests verify multiple attempts
- [ ] All tests pass
- [ ] Coverage ≥80% for ui.py

**Estimated Complexity:** Medium

**Dependencies:** TASK-013

---

### TASK-015: Implement Main Entry Point

**Title:** Create main.py with application entry point and initialization

**Description:**
Implement the main() function that serves as the application entry point, initializes the task list, and sets up exception handling.

**Preconditions:**
- TASK-013 complete
- ui.py and operations.py fully implemented

**Specification References:**
- PHASE_I_SPECIFICATION.md: "CLI Interaction Flow" - Application Start
- US-107: Exit Application

**Plan References:**
- PHASE_I_PLAN.md: Section 4.1 "Application Lifecycle"
- PHASE_I_PLAN.md: Section 5.4 "Layer 4: Application Orchestration (main.py)"

**Artifacts to Create:**
```
phase_i/main.py
```

**Implementation Requirements:**

```python
import sys
from typing import List
from phase_i.models import Task
from phase_i import ui


def main() -> None:
    """
    Application entry point.

    Initializes task list, displays welcome screen,
    and starts the main menu loop.
    """
    # Check Python version
    if sys.version_info < (3, 11):
        print("Error: Python 3.11 or higher required")
        sys.exit(1)

    # Initialize empty task list
    tasks: List[Task] = []

    try:
        # Display welcome screen
        ui.display_welcome()

        # Start menu loop
        run_menu_loop(tasks)

    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        sys.exit(0)

    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        print("Please restart the application.")
        sys.exit(1)


def run_menu_loop(tasks: List[Task]) -> None:
    """
    Main menu loop - runs until user exits.

    Args:
        tasks: Task list (shared across all operations)
    """
    # TODO: Implement in TASK-016
    pass


if __name__ == "__main__":
    main()
```

**Acceptance Criteria:**
- [ ] `phase_i/main.py` exists
- [ ] `main()` function implemented
- [ ] Python version check (3.11+) included
- [ ] Empty task list initialized as `List[Task]`
- [ ] Welcome screen displayed via ui.display_welcome()
- [ ] run_menu_loop() called with tasks
- [ ] KeyboardInterrupt (Ctrl+C) caught and handled gracefully
- [ ] Generic Exception caught with error message
- [ ] `if __name__ == "__main__"` guard present
- [ ] run_menu_loop() defined (stub for TASK-016)
- [ ] All imports correct
- [ ] Type hints on all functions
- [ ] Docstrings present
- [ ] Can run: `python phase_i/main.py` (exits immediately, no menu yet)

**Estimated Complexity:** Small

**Dependencies:** TASK-013

---

### TASK-016: Implement Menu Loop

**Title:** Create menu loop in main.py

**Description:**
Implement the run_menu_loop() function that displays the menu, captures user choice, and routes to the appropriate handler.

**Preconditions:**
- TASK-015 complete
- main.py exists with main() and run_menu_loop() stub

**Specification References:**
- PHASE_I_SPECIFICATION.md: "CLI Interaction Flow" - Main Menu

**Plan References:**
- PHASE_I_PLAN.md: Section 4.2 "Menu Loop Implementation"

**Artifacts to Modify:**
```
phase_i/main.py
```

**Implementation Requirements:**

```python
def run_menu_loop(tasks: List[Task]) -> None:
    """
    Main menu loop - runs until user exits.

    Args:
        tasks: Task list (shared across all operations)
    """
    while True:
        ui.display_menu()
        choice = ui.get_menu_choice()

        if choice == 1:
            handle_add_task(tasks)
        elif choice == 2:
            handle_view_tasks(tasks)
        elif choice == 3:
            handle_update_task(tasks)
        elif choice == 4:
            handle_delete_task(tasks)
        elif choice == 5:
            handle_mark_complete(tasks)
        elif choice == 6:
            handle_mark_incomplete(tasks)
        elif choice == 7:
            ui.display_goodbye()
            break  # Exit loop


# Handler stubs (implemented in TASK-017)
def handle_add_task(tasks: List[Task]) -> None:
    """Handle Add Task menu option."""
    pass


def handle_view_tasks(tasks: List[Task]) -> None:
    """Handle View Tasks menu option."""
    pass


def handle_update_task(tasks: List[Task]) -> None:
    """Handle Update Task menu option."""
    pass


def handle_delete_task(tasks: List[Task]) -> None:
    """Handle Delete Task menu option."""
    pass


def handle_mark_complete(tasks: List[Task]) -> None:
    """Handle Mark Task Complete menu option."""
    pass


def handle_mark_incomplete(tasks: List[Task]) -> None:
    """Handle Mark Task Incomplete menu option."""
    pass
```

**Acceptance Criteria:**
- [ ] `run_menu_loop()` implemented with infinite loop
- [ ] Menu displayed each iteration
- [ ] User choice captured via ui.get_menu_choice()
- [ ] Choice routed to correct handler (1-7)
- [ ] Choice 7 displays goodbye and breaks loop
- [ ] All 6 handler functions defined (stubs for TASK-017)
- [ ] Handler stubs have type hints and docstrings
- [ ] Can run application: `python phase_i/main.py`
- [ ] Menu displays, accepts choice 7 to exit
- [ ] Other choices (1-6) return to menu without error

**Estimated Complexity:** Small

**Dependencies:** TASK-015

---

### TASK-017: Implement Handler Functions

**Title:** Create all feature handler functions in main.py

**Description:**
Implement all 6 handler functions that connect the UI layer to the operations layer for each menu option.

**Preconditions:**
- TASK-016 complete
- main.py has menu loop with handler stubs

**Specification References:**
- PHASE_I_SPECIFICATION.md: User Stories US-101 through US-106
- "Feature Interaction Flows" section

**Plan References:**
- PHASE_I_PLAN.md: Section 4.4 "Feature Handler Pattern"

**Artifacts to Modify:**
```
phase_i/main.py
```

**Implementation Requirements:**

```python
from phase_i import operations


def handle_add_task(tasks: List[Task]) -> None:
    """Handle Add Task menu option."""
    print("\n--- Add New Task ---")

    description = ui.get_task_description()
    success, message, new_task = operations.add_task(tasks, description)

    if success:
        ui.display_success(message)
    else:
        ui.display_error(message)

    ui.pause()


def handle_view_tasks(tasks: List[Task]) -> None:
    """Handle View Tasks menu option."""
    print("\n--- Your Task List ---")
    ui.display_tasks(tasks)
    ui.pause()


def handle_update_task(tasks: List[Task]) -> None:
    """Handle Update Task menu option."""
    print("\n--- Update Task ---")

    task_id = ui.get_task_id()

    # Show current task
    task = operations.get_task_by_id(tasks, task_id)
    if not task:
        ui.display_error(f"Task with ID {task_id} not found")
        ui.pause()
        return

    print(f'\nCurrent task: "{task.description}"')
    new_description = ui.get_task_description()

    success, message = operations.update_task(tasks, task_id, new_description)

    if success:
        ui.display_success(message)
    else:
        ui.display_error(message)

    ui.pause()


def handle_delete_task(tasks: List[Task]) -> None:
    """Handle Delete Task menu option."""
    print("\n--- Delete Task ---")

    task_id = ui.get_task_id()

    # Show task to be deleted
    task = operations.get_task_by_id(tasks, task_id)
    if not task:
        ui.display_error(f"Task with ID {task_id} not found")
        ui.pause()
        return

    print(f'\nTask to delete: ID {task.id} - "{task.description}"')
    confirmed = ui.get_confirmation()

    if confirmed:
        success, message = operations.delete_task(tasks, task_id)
        if success:
            ui.display_success(message)
        else:
            ui.display_error(message)
    else:
        print("\nDelete cancelled")

    ui.pause()


def handle_mark_complete(tasks: List[Task]) -> None:
    """Handle Mark Task Complete menu option."""
    print("\n--- Mark Task Complete ---")

    task_id = ui.get_task_id()
    success, message = operations.mark_complete(tasks, task_id)

    if success:
        ui.display_success(message)
    else:
        ui.display_error(message)

    ui.pause()


def handle_mark_incomplete(tasks: List[Task]) -> None:
    """Handle Mark Task Incomplete menu option."""
    print("\n--- Mark Task Incomplete ---")

    task_id = ui.get_task_id()
    success, message = operations.mark_incomplete(tasks, task_id)

    if success:
        ui.display_success(message)
    else:
        ui.display_error(message)

    ui.pause()
```

**Acceptance Criteria:**
- [ ] `handle_add_task()` fully implemented per US-101
- [ ] `handle_view_tasks()` fully implemented per US-102
- [ ] `handle_update_task()` fully implemented per US-103
- [ ] handle_update_task shows current task before update
- [ ] `handle_delete_task()` fully implemented per US-104
- [ ] handle_delete_task shows task before deletion
- [ ] handle_delete_task asks for confirmation
- [ ] handle_delete_task respects Y/N confirmation
- [ ] `handle_mark_complete()` fully implemented per US-105
- [ ] `handle_mark_incomplete()` fully implemented per US-106
- [ ] All handlers display section headers
- [ ] All handlers display success/error messages appropriately
- [ ] All handlers call ui.pause() before returning
- [ ] All handlers have docstrings
- [ ] Can run full application: `python phase_i/main.py`
- [ ] All 7 menu options work end-to-end

**Estimated Complexity:** Medium

**Dependencies:** TASK-016

---

### TASK-018: Add Exception Handling

**Title:** Verify and enhance exception handling in main.py

**Description:**
Ensure robust exception handling is in place for all error scenarios including keyboard interrupts and unexpected errors.

**Preconditions:**
- TASK-017 complete
- All handler functions implemented

**Specification References:**
- PHASE_I_SPECIFICATION.md: "Error Handling" section
- "Acceptance Criteria" - Application starts and exits cleanly

**Plan References:**
- PHASE_I_PLAN.md: Section 6 "Error Handling Strategy"
- Section 6.4 "No-Crash Guarantee"

**Artifacts to Modify:**
```
phase_i/main.py
```

**Implementation Requirements:**

Verify that main() has proper exception handling:
- KeyboardInterrupt caught and handled gracefully
- Generic Exception caught with error message
- Application never crashes from user input

Add any additional error handling if needed in handler functions.

**Testing Requirements:**
- Test Ctrl+C during menu prompt
- Test Ctrl+C during input prompt
- Verify no crashes from any user input combination

**Acceptance Criteria:**
- [ ] KeyboardInterrupt handler in main() displays message and exits gracefully
- [ ] Generic exception handler catches unexpected errors
- [ ] No crashes possible from invalid user input
- [ ] All input validation loops prevent invalid data from reaching handlers
- [ ] Manual testing: Ctrl+C exits cleanly with message
- [ ] Manual testing: All error cases in spec handled without crashes
- [ ] Application exits with appropriate exit codes (0 for normal, 1 for error)

**Estimated Complexity:** Small

**Dependencies:** TASK-017

---

### TASK-019: Write Integration Tests

**Title:** Create end-to-end integration tests

**Description:**
Write integration tests that verify complete user flows from start to finish, testing the interaction between all layers.

**Preconditions:**
- TASK-018 complete
- Full application functional

**Specification References:**
- PHASE_I_SPECIFICATION.md: "Testing Requirements" - Integration Tests

**Plan References:**
- PHASE_I_PLAN.md: Section 7.2 "Testing Strategy" - Integration Testing

**Artifacts to Create:**
```
tests/phase_i/test_integration.py
```

**Test Cases to Implement:**

1. `test_add_and_view_flow()` - Add task, then view list
2. `test_add_update_view_flow()` - Add task, update it, view list
3. `test_add_delete_view_flow()` - Add task, delete it, view empty list
4. `test_add_mark_complete_view_flow()` - Add task, mark complete, view with status
5. `test_add_mark_incomplete_flow()` - Add complete task, mark incomplete
6. `test_multiple_tasks_flow()` - Add multiple tasks, view all
7. `test_update_nonexistent_task()` - Try to update invalid ID, verify error
8. `test_delete_nonexistent_task()` - Try to delete invalid ID, verify error
9. `test_delete_with_confirmation_no()` - Delete with 'N' confirmation, task remains
10. `test_id_generation_after_delete()` - Delete task, add new task, verify ID increments
11. `test_empty_list_operations()` - View empty list, try operations on empty list
12. `test_complete_user_session()` - Full session: add multiple, update, delete, mark complete

**Implementation Notes:**
```python
from phase_i.models import Task
from phase_i import operations


def test_add_and_view_flow():
    """Test adding a task and viewing it."""
    tasks = []

    # Add task
    success, message, task = operations.add_task(tasks, "Buy groceries")
    assert success is True
    assert len(tasks) == 1
    assert tasks[0].description == "Buy groceries"

    # View tasks
    all_tasks = operations.get_all_tasks(tasks)
    assert len(all_tasks) == 1
    assert all_tasks[0].id == 1


def test_add_update_view_flow():
    """Test adding, updating, and viewing a task."""
    tasks = []

    # Add task
    success, message, task = operations.add_task(tasks, "Original description")
    assert success is True
    task_id = task.id

    # Update task
    success, message = operations.update_task(tasks, task_id, "Updated description")
    assert success is True
    assert tasks[0].description == "Updated description"

    # View tasks
    all_tasks = operations.get_all_tasks(tasks)
    assert all_tasks[0].description == "Updated description"
```

**Acceptance Criteria:**
- [ ] `tests/phase_i/test_integration.py` exists
- [ ] All 12 integration test cases implemented
- [ ] Tests cover complete user flows
- [ ] Tests verify data flows between layers correctly
- [ ] Tests verify error handling end-to-end
- [ ] All tests pass
- [ ] Tests use actual operations (no mocking between layers)
- [ ] Tests verify state changes persist correctly

**Estimated Complexity:** Medium

**Dependencies:** TASK-018

---

### TASK-020: Quality Assurance - Linting, Formatting, Coverage

**Title:** Run quality checks and ensure all standards met

**Description:**
Run all quality assurance tools including linting (Ruff), formatting (Black), and coverage reporting. Fix any issues found.

**Preconditions:**
- TASK-019 complete
- All code and tests implemented

**Specification References:**
- PHASE_I_SPECIFICATION.md: "Acceptance Criteria" - Quality Gates

**Plan References:**
- PHASE_I_PLAN.md: Section 8.4 "Code Quality Tools"
- Section 11 "Success Criteria"

**Artifacts to Modify:**
- Any files with linting/formatting issues

**Quality Checks to Perform:**

1. **Install tools (if needed):**
```bash
pip install ruff black pytest pytest-cov
```

2. **Run Black formatting:**
```bash
black phase_i/ tests/
```

3. **Run Ruff linting:**
```bash
ruff check phase_i/ tests/
```

4. **Run all tests with coverage:**
```bash
pytest tests/phase_i/ --cov=phase_i --cov-report=term-missing
```

5. **Verify type hints:**
```bash
# All functions should have type hints
# Manual review or use mypy if available
```

**Acceptance Criteria:**
- [ ] Black formatting applied to all Python files
- [ ] Ruff linting passes with no errors
- [ ] All tests pass: `pytest tests/phase_i/`
- [ ] Test coverage ≥80%: `pytest --cov=phase_i --cov-report=term`
- [ ] Coverage report shows which lines covered
- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] No commented-out code
- [ ] No TODO comments
- [ ] No hardcoded values that should be constants

**Estimated Complexity:** Small

**Dependencies:** TASK-019

---

### TASK-021: Manual Testing and Documentation

**Title:** Perform manual testing and create user documentation

**Description:**
Execute the manual testing checklist from the specification, verify all user stories work correctly, and create user-facing documentation.

**Preconditions:**
- TASK-020 complete
- All quality checks passed

**Specification References:**
- PHASE_I_SPECIFICATION.md: "Testing Requirements" - Manual Testing Checklist
- All User Stories (US-101 through US-107)

**Plan References:**
- PHASE_I_PLAN.md: Section 7.2 "Testing Strategy" - Manual Testing

**Artifacts to Create:**
```
README_PHASE_I.md
```

**Manual Testing Checklist:**

Execute each item and verify behavior:
- [ ] Application starts without errors
- [ ] Main menu displays correctly
- [ ] Can add task with valid description
- [ ] Cannot add task with empty description
- [ ] Cannot add task with >500 char description
- [ ] View tasks shows correct format
- [ ] View tasks handles empty list
- [ ] Can update existing task
- [ ] Cannot update non-existent task
- [ ] Can delete task with confirmation
- [ ] Delete respects Y/N confirmation
- [ ] Cannot delete non-existent task
- [ ] Can mark task complete
- [ ] Can mark task incomplete
- [ ] Complete/incomplete handles non-existent ID
- [ ] Invalid menu choices show error
- [ ] Exit option terminates cleanly
- [ ] Ctrl+C exits gracefully

**User Documentation to Create:**

Create `README_PHASE_I.md` with:
1. Project overview
2. Requirements (Python 3.11+)
3. Installation/setup instructions
4. How to run: `python phase_i/main.py`
5. Feature list (7 features)
6. Usage examples for each feature
7. Known limitations
8. Phase I completion status

**Documentation Template:**
```markdown
# Phase I - Todo List Manager

## Overview
Simple in-memory console-based todo list application.

## Requirements
- Python 3.11 or higher
- No external dependencies

## Installation
No installation required. Clone repository and run.

## Usage
Start the application:
```
python phase_i/main.py
```

## Features
1. Add Task - Create new tasks
2. View Tasks - Display all tasks
3. Update Task - Modify task description
4. Delete Task - Remove tasks
5. Mark Complete - Mark tasks as done
6. Mark Incomplete - Reopen completed tasks
7. Exit - Close application

## Examples
[Usage examples for each feature]

## Limitations
- In-memory only (data lost on exit)
- Single user
- No persistence
- Basic features only

## Testing
Run tests:
```
pytest tests/phase_i/
```

## Phase I Status
✅ COMPLETE - All acceptance criteria met
```

**Acceptance Criteria:**
- [ ] All 18 manual testing checklist items verified
- [ ] All user stories tested end-to-end
- [ ] `README_PHASE_I.md` created with complete documentation
- [ ] README includes requirements, usage, features, examples
- [ ] README includes how to run application
- [ ] README includes how to run tests
- [ ] All features demonstrated and working
- [ ] Application ready for user acceptance testing

**Estimated Complexity:** Small

**Dependencies:** TASK-020

---

## TASK SUMMARY

**Total Tasks:** 21

**By Complexity:**
- Small: 18 tasks
- Medium: 3 tasks (TASK-014, TASK-017, TASK-019)

**By Category:**
- Project Setup: 1 task (TASK-001)
- Data Model: 2 tasks (TASK-002, TASK-003)
- Operations Layer: 7 tasks (TASK-004 through TASK-011)
- Presentation Layer: 3 tasks (TASK-012, TASK-013, TASK-014)
- Application Layer: 4 tasks (TASK-015 through TASK-018)
- Testing & QA: 4 tasks (TASK-019 through TASK-021)

**Sequential Dependencies:**
All tasks must be completed in order due to dependencies.

**Estimated Total Effort:**
- Small tasks: ~1-2 hours each
- Medium tasks: ~2-4 hours each
- Total: ~30-40 hours for full Phase I implementation

---

## COMPLETION VERIFICATION

Phase I is complete when:

1. ✅ All 21 tasks have "Acceptance Criteria" checked
2. ✅ All tests pass (unit + integration)
3. ✅ Coverage ≥80%
4. ✅ Linting passes (Ruff)
5. ✅ Formatting applied (Black)
6. ✅ Manual testing checklist 100% complete
7. ✅ README documentation created
8. ✅ Application runs without errors
9. ✅ All 7 user stories functional
10. ✅ Constitutional compliance verified

---

## AGENT IMPLEMENTATION NOTES

### What Agents MUST Do:
- Implement tasks sequentially in order
- Complete all acceptance criteria before marking task done
- Write tests during implementation, not after
- Follow specification and plan exactly
- Reference spec/plan sections in code comments where helpful
- Ask for clarification if any ambiguity exists

### What Agents MUST NOT Do:
- Skip tasks or reorder without justification
- Add features not in specification
- Make architectural changes not in plan
- Skip acceptance criteria
- Implement multiple tasks simultaneously (unless independent)
- Deviate from specifications

### Clarification Protocol:
If any task is unclear:
1. STOP implementation
2. Document specific ambiguity
3. Reference relevant spec/plan sections
4. Request clarification
5. Wait for response before proceeding

---

## APPROVAL AND READINESS

**Task Breakdown Status:** APPROVED
**Constitutional Compliance:** VERIFIED
**Specification Compliance:** VERIFIED
**Plan Compliance:** VERIFIED
**Ready for Implementation:** YES

**Next Steps:**
1. Assign TASK-001 to implementation agent
2. Begin implementation per constitutional workflow
3. Complete tasks sequentially
4. Verify acceptance criteria after each task
5. Proceed to next task only when current task complete

---

**END OF PHASE I TASK BREAKDOWN**

*These tasks implement ONLY the requirements specified in PHASE_I_SPECIFICATION.md and PHASE_I_PLAN.md. All tasks are subordinate to CONSTITUTION.md. No implementation may deviate from these tasks without specification/plan amendment.*
