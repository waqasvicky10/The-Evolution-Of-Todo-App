# PHASE I TECHNICAL IMPLEMENTATION PLAN

**Project:** Evolution of Todo
**Phase:** I - Foundation
**Version:** 1.0
**Status:** APPROVED
**Parent Document:** PHASE_I_SPECIFICATION.md
**Constitutional Compliance:** Verified against CONSTITUTION.md
**Date:** 2025-12-29

---

## EXECUTIVE SUMMARY

This document defines the technical implementation approach for Phase I of the Evolution of Todo project. It describes HOW the approved Phase I specification will be implemented, without introducing new features or deviating from constitutional requirements.

---

## CONSTITUTIONAL COMPLIANCE

This plan is created under:
- **Article I, Section 1.3:** Plan Requirements
- **Article II, Section 2.2:** Strict Specification Adherence
- **Article III, Section 3.1:** Phase Scope Boundaries
- **Constitutional Workflow:** Constitution → Spec → **Plan** → Tasks → Code

This plan implements ONLY what is specified in PHASE_I_SPECIFICATION.md.

---

## PLANNING PRINCIPLES

### What This Plan Does
✅ Describes technical implementation approach
✅ Defines data structures and algorithms
✅ Specifies module responsibilities
✅ Documents control flow and error handling
✅ Breaks work into implementable components
✅ Ensures architectural compliance

### What This Plan Does NOT Do
❌ Add new features beyond specification
❌ Make architectural decisions not in spec
❌ Reference future phases
❌ Introduce external dependencies
❌ Change specified behavior

---

## 1. HIGH-LEVEL APPLICATION STRUCTURE

### 1.1 Overview

Phase I is a **single-process, in-memory Python console application** with no external dependencies. The application runs in a continuous loop until the user explicitly exits.

**Runtime Characteristics:**
- Single Python interpreter process
- In-memory task storage (Python list)
- Synchronous execution (no concurrency)
- Terminal-based interaction
- Session-scoped data (lost on exit)

### 1.2 Module Architecture

```
phase_i/
├── __init__.py          # Package marker (empty)
├── main.py              # Entry point + application orchestration
├── models.py            # Task data model + validation
├── operations.py        # Business logic + CRUD operations
└── ui.py                # CLI display + input handling
```

**Module Dependency Graph:**
```
main.py
  ├─→ ui.py
  │     └─→ operations.py
  │           └─→ models.py
  └─→ operations.py
        └─→ models.py
```

**Execution Flow:**
1. Python interpreter executes `python phase_i/main.py`
2. `main.py` initializes empty task list
3. `main.py` displays welcome screen via `ui.py`
4. `main.py` enters menu loop
5. Menu loop continues until user selects Exit
6. Application terminates, memory released

### 1.3 Module Responsibilities

| Module | Responsibility | Depends On | Used By |
|--------|---------------|------------|---------|
| `models.py` | Task entity definition, field validation | None (pure Python) | `operations.py` |
| `operations.py` | CRUD logic, task list manipulation | `models.py` | `main.py`, `ui.py` |
| `ui.py` | Display formatting, input capture | `operations.py` (for display only) | `main.py` |
| `main.py` | App lifecycle, menu coordination | `ui.py`, `operations.py` | None (entry point) |

### 1.4 Execution Context

**Global State:**
- Single task list: `tasks: List[Task]` (initialized in `main()`)
- Next ID counter: Derived from `len(tasks) + 1`

**State Management:**
- Task list passed explicitly to all functions (no global variables)
- Functions modify list in-place (mutable list operations)
- No state persistence between application runs

---

## 2. IN-MEMORY DATA STRUCTURES

### 2.1 Task Storage Structure

**Primary Data Structure:** Python `list` of `Task` objects

```python
# Runtime structure
tasks: List[Task] = []

# Example populated state
tasks = [
    Task(id=1, description="Buy groceries", is_complete=False),
    Task(id=2, description="Finish homework", is_complete=True),
    Task(id=3, description="Call dentist", is_complete=False)
]
```

**Rationale:**
- Simple append operation for add
- Linear search acceptable for small lists (<1000 tasks)
- Order preservation (insertion order = ID order)
- Direct index access for iteration

### 2.2 Task Entity Definition

**Implementation: Python `dataclass`**

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    """
    Represents a single todo task.

    Attributes:
        id: Unique positive integer identifier
        description: Task description (1-500 characters)
        is_complete: Task completion status
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
```

**Field Storage:**
- `id`: Python `int` (native integer type)
- `description`: Python `str` (Unicode string)
- `is_complete`: Python `bool` (`True` or `False`)

**Memory Estimate:**
- Task object overhead: ~56 bytes
- Description (avg 50 chars): ~100 bytes
- Total per task: ~156 bytes
- 1000 tasks: ~156 KB (well within spec: <10MB)

### 2.3 Data Structure Operations

| Operation | Method | Time Complexity | Implementation |
|-----------|--------|-----------------|----------------|
| Add task | `tasks.append(task)` | O(1) | Python list append |
| Get all tasks | `return tasks` | O(1) | Direct reference |
| Find by ID | Linear search | O(n) | `next((t for t in tasks if t.id == id), None)` |
| Update task | Find + modify | O(n) | Find task, update fields |
| Delete task | Find + remove | O(n) | `tasks.remove(task)` |
| Count tasks | `len(tasks)` | O(1) | Python list length |

**Performance Notes:**
- All operations are acceptable for specification requirement (<1000 tasks, <100ms)
- No indexing/caching needed for Phase I
- Linear search sufficient given small dataset

### 2.4 Alternative Considered (Not Chosen)

**Dictionary-based storage:** `Dict[int, Task]`
- **Pros:** O(1) lookup by ID
- **Cons:** More complex, harder to maintain order, unnecessary optimization
- **Decision:** Rejected - premature optimization, list is sufficient

---

## 3. TASK IDENTIFICATION STRATEGY

### 3.1 ID Generation Algorithm

**Strategy:** Sequential auto-increment starting from 1

**Algorithm:**
```python
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

**Rationale:**
- Simple and predictable
- No need for UUID/random IDs (single user, in-memory)
- IDs remain sequential even after deletions
- User-friendly (small, readable numbers)

### 3.2 ID Management Rules

**Creation:**
- ID assigned at task creation time
- User never specifies ID manually
- ID generation called before Task instantiation

**Immutability:**
- Task IDs never change after creation
- No ID reuse after deletion
- ID sequence may have gaps after deletions

**Validation:**
- User-provided IDs (for update/delete/mark) validated as integers
- Existence check performed before operations
- Error messages include invalid ID for debugging

### 3.3 ID Usage Patterns

**Add Task:**
```python
next_id = get_next_id(tasks)
new_task = Task(id=next_id, description=user_input)
tasks.append(new_task)
```

**Find Task:**
```python
task = next((t for t in tasks if t.id == target_id), None)
if task is None:
    # Handle error
```

**Edge Cases:**
- Empty list → ID = 1
- Deleted task 2 from [1,2,3] → Next ID = 4 (not 2)
- 1000 tasks → Next ID = 1001

---

## 4. CLI CONTROL FLOW

### 4.1 Application Lifecycle

```
[START]
   ↓
Initialize empty task list
   ↓
Display welcome screen
   ↓
┌─────────────────────────┐
│   MENU LOOP (infinite)  │
│  ┌──────────────────┐   │
│  │ Display menu     │   │
│  │ Get user choice  │   │
│  │ Validate choice  │   │
│  │ Route to handler │   │
│  │ Execute feature  │   │
│  │ Return to menu   │   │
│  └──────────────────┘   │
│         ↓ (Exit chosen) │
└─────────────────────────┘
   ↓
Display goodbye message
   ↓
[END]
```

### 4.2 Menu Loop Implementation

**Pseudocode:**
```python
def run_menu_loop(tasks: List[Task]) -> None:
    """Main menu loop - runs until user exits."""
    while True:
        display_menu()
        choice = get_menu_choice()

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
            display_goodbye()
            break  # Exit loop
```

**Loop Characteristics:**
- Infinite loop (`while True`)
- Single exit condition (choice == 7)
- No timeout or automatic exit
- Each iteration is one menu interaction

### 4.3 Input Handling Strategy

**Menu Choice Input:**
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
                display_error("Invalid choice. Please enter 1-7.")
        except ValueError:
            display_error("Invalid choice. Please enter 1-7.")
```

**Task ID Input:**
```python
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
```

**Task Description Input:**
```python
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
            display_error("Task description too long (max 500)")
        else:
            return description
```

**Confirmation Input:**
```python
def get_confirmation() -> bool:
    """
    Prompt user for Y/N confirmation.

    Returns:
        True if confirmed, False otherwise
    """
    while True:
        user_input = input("Are you sure? (Y/N): ").strip().upper()

        if user_input in ['Y', 'YES']:
            return True
        elif user_input in ['N', 'NO']:
            return False
        else:
            display_error("Please enter Y or N")
```

### 4.4 Feature Handler Pattern

Each menu option has a dedicated handler function in `main.py`:

**Handler Template:**
```python
def handle_<feature>(tasks: List[Task]) -> None:
    """
    Handle <feature> menu option.

    Args:
        tasks: Task list (modified in-place if needed)
    """
    # 1. Display feature header
    print("\n--- <Feature Name> ---")

    # 2. Get user input via ui.py
    user_input = ui.get_<input_type>()

    # 3. Call business logic via operations.py
    success, message, result = operations.<operation>(tasks, user_input)

    # 4. Display result
    if success:
        ui.display_success(message)
    else:
        ui.display_error(message)

    # 5. Pause before returning to menu
    ui.pause()
```

**Example - Add Task Handler:**
```python
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
```

### 4.5 Control Flow Characteristics

**Synchronous Execution:**
- No async/await (not needed)
- Blocking input calls (wait for user)
- Single-threaded operation

**Error Recovery:**
- Invalid input re-prompts (input validation loops)
- Errors display and return to menu
- No application crashes from user input

**State Isolation:**
- Each handler is independent
- Task list is shared reference
- No global state beyond task list

---

## 5. SEPARATION OF RESPONSIBILITIES

### 5.1 Layered Architecture Implementation

**Layer 1: Domain Model (models.py)**

**Responsibilities:**
- Define Task entity structure
- Enforce data constraints
- Provide validation functions

**What it DOES:**
- Create Task instances
- Validate field values
- Raise errors for invalid data

**What it DOES NOT do:**
- Access task list
- Perform CRUD operations
- Handle user input/output
- Contain business logic

**Key Functions:**
```python
@dataclass
class Task:
    """Task entity definition"""
    pass

def validate_description(description: str) -> bool:
    """Validate task description constraints."""
    return 1 <= len(description) <= 500
```

---

**Layer 2: Business Logic (operations.py)**

**Responsibilities:**
- Implement CRUD operations
- Manage task list manipulation
- Enforce business rules
- Return structured results

**What it DOES:**
- Add/update/delete tasks from list
- Find tasks by ID
- Generate next ID
- Validate business constraints
- Return (success, message, data) tuples

**What it DOES NOT do:**
- Display output to user
- Capture user input
- Format display text
- Handle menu logic

**Key Functions:**
```python
def add_task(tasks: List[Task], description: str) -> Tuple[bool, str, Optional[Task]]:
    """
    Add new task to list.

    Args:
        tasks: Task list (modified in-place)
        description: Task description

    Returns:
        (success, message, created_task)
    """
    if not validate_description(description):
        return (False, "Invalid description", None)

    next_id = get_next_id(tasks)
    new_task = Task(id=next_id, description=description)
    tasks.append(new_task)

    return (True, f"Task added with ID {next_id}", new_task)

def get_task_by_id(tasks: List[Task], task_id: int) -> Optional[Task]:
    """Find task by ID."""
    return next((t for t in tasks if t.id == task_id), None)

def update_task(tasks: List[Task], task_id: int, new_desc: str) -> Tuple[bool, str]:
    """Update task description."""
    task = get_task_by_id(tasks, task_id)
    if not task:
        return (False, f"Task with ID {task_id} not found")

    if not validate_description(new_desc):
        return (False, "Invalid description")

    task.description = new_desc
    return (True, f"Task {task_id} updated")
```

---

**Layer 3: Presentation (ui.py)**

**Responsibilities:**
- Display formatted output
- Capture and validate user input
- Format error/success messages
- Render task lists

**What it DOES:**
- Print menus and headers
- Get input from stdin
- Format task list display
- Show error/success messages
- Pause for user acknowledgment

**What it DOES NOT do:**
- Modify task list
- Implement business logic
- Make business decisions
- Access Task internals (uses operations for data)

**Key Functions:**
```python
def display_menu() -> None:
    """Display main menu."""
    print("\n" + "="*40)
    print("           MAIN MENU")
    print("="*40)
    print("1. Add Task")
    # ... etc

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

def get_task_description() -> str:
    """Prompt and validate task description."""
    # Input validation loop (see section 4.3)
    pass

def display_error(message: str) -> None:
    """Display error message."""
    print(f"\nError: {message}")

def pause() -> None:
    """Wait for user acknowledgment."""
    input("\nPress Enter to continue...")
```

---

**Layer 4: Application Orchestration (main.py)**

**Responsibilities:**
- Application entry point
- Initialize task list
- Coordinate menu loop
- Connect UI and operations
- Handle application lifecycle

**What it DOES:**
- Run main loop
- Route menu choices to handlers
- Pass data between layers
- Handle Ctrl+C gracefully

**What it DOES NOT do:**
- Implement business logic
- Format output directly
- Validate input directly
- Define data structures

**Key Functions:**
```python
def main() -> None:
    """Application entry point."""
    tasks: List[Task] = []  # Initialize empty list

    try:
        ui.display_welcome()
        run_menu_loop(tasks)
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)

def run_menu_loop(tasks: List[Task]) -> None:
    """Main menu loop."""
    # See section 4.2
    pass

def handle_add_task(tasks: List[Task]) -> None:
    """Add task handler."""
    # See section 4.4
    pass

# ... other handlers

if __name__ == "__main__":
    main()
```

### 5.2 Interface Contracts

**operations.py → models.py:**
```python
# operations.py imports and uses Task
from models import Task, validate_description
```

**ui.py → No direct model access:**
```python
# ui.py does NOT import models
# Receives tasks as List[Task] for display only
# Does not create or modify Task objects
```

**main.py → ui.py + operations.py:**
```python
# main.py imports both
from models import Task
from operations import add_task, get_all_tasks, ...
from ui import display_menu, get_task_description, ...
```

### 5.3 Dependency Rules

**Allowed Dependencies:**
- main.py → ui.py ✅
- main.py → operations.py ✅
- ui.py → operations.py ✅ (read-only, for display)
- operations.py → models.py ✅

**Prohibited Dependencies:**
- models.py → anything ❌
- operations.py → ui.py ❌
- operations.py → main.py ❌
- ui.py → models.py ❌ (gets Task via parameters)

**Rationale:**
- Inner layers independent of outer layers
- Easy to test (mock outer dependencies)
- Clear responsibility boundaries
- No circular dependencies

---

## 6. ERROR HANDLING STRATEGY

### 6.1 Error Handling Layers

**Layer 1: Input Validation (ui.py)**

**Strategy:** Re-prompt until valid input received

```python
def get_menu_choice() -> int:
    """Returns valid menu choice (1-7) - never returns invalid value."""
    while True:  # Loop until valid
        try:
            choice = int(input("Enter choice (1-7): ").strip())
            if 1 <= choice <= 7:
                return choice  # Valid - exit loop
            else:
                display_error("Invalid choice. Please enter 1-7.")
        except ValueError:
            display_error("Invalid choice. Please enter 1-7.")
        # Loop continues on error
```

**Characteristics:**
- Never returns invalid data
- User cannot proceed without valid input
- No exceptions propagated to caller
- Clear error messages displayed

---

**Layer 2: Business Logic Validation (operations.py)**

**Strategy:** Return (success, message, data) tuples

```python
def add_task(tasks: List[Task], description: str) -> Tuple[bool, str, Optional[Task]]:
    """
    Returns:
        (True, success_message, task) on success
        (False, error_message, None) on failure
    """
    if not description or len(description) > 500:
        return (False, "Invalid description length", None)

    # Success path
    task = Task(...)
    tasks.append(task)
    return (True, f"Task {task.id} added", task)
```

**Characteristics:**
- No exceptions for business rule violations
- Caller decides how to handle errors
- Consistent return format
- Error messages ready for display

---

**Layer 3: Application Coordination (main.py)**

**Strategy:** Check operation results, display appropriate messages

```python
def handle_add_task(tasks: List[Task]) -> None:
    """Coordinates UI and operations."""
    description = ui.get_task_description()  # Always valid (validated in ui)

    success, message, task = operations.add_task(tasks, description)

    if success:
        ui.display_success(message)
    else:
        ui.display_error(message)

    ui.pause()
    # Return to menu - no crash
```

**Characteristics:**
- Handles success/error uniformly
- Always returns to menu (no crashes)
- Delegates display to ui.py
- Simple conditional logic

---

### 6.2 Error Categories and Handling

**Category 1: Invalid Input Format**

**Examples:**
- Menu choice is "abc" (not a number)
- Task ID is "xyz" (not an integer)

**Handling:**
```python
try:
    value = int(user_input)
except ValueError:
    display_error("Must be a number")
    # Re-prompt in loop
```

**Location:** ui.py input functions

---

**Category 2: Invalid Input Value**

**Examples:**
- Menu choice is 10 (out of range 1-7)
- Task description is empty
- Task description is 501 characters

**Handling:**
```python
if not (1 <= choice <= 7):
    display_error("Choice must be 1-7")
    # Re-prompt in loop

if not description.strip():
    display_error("Description cannot be empty")
    # Re-prompt in loop
```

**Location:** ui.py validation logic

---

**Category 3: Business Rule Violations**

**Examples:**
- Task ID not found
- Cannot update non-existent task
- Cannot delete non-existent task

**Handling:**
```python
task = get_task_by_id(tasks, task_id)
if not task:
    return (False, f"Task with ID {task_id} not found")
    # Caller displays error and returns to menu
```

**Location:** operations.py functions

---

**Category 4: Informational Messages**

**Examples:**
- Task already marked complete
- Task already marked incomplete

**Handling:**
```python
if task.is_complete:
    return (True, f"Info: Task {task_id} is already complete")
    # Treated as success, informational message
```

**Location:** operations.py functions

---

**Category 5: System Errors**

**Examples:**
- Keyboard interrupt (Ctrl+C)
- Unexpected exceptions

**Handling:**
```python
def main() -> None:
    try:
        # Run application
        run_menu_loop(tasks)
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        print("Please restart the application.")
        sys.exit(1)
```

**Location:** main.py main() function

---

### 6.3 Error Messages

**Format:** Clear, actionable, user-friendly

**Template:** `"Error: <what went wrong> (<how to fix>)"`

**Examples:**
```python
"Error: Invalid choice. Please enter a number between 1 and 7."
"Error: Task ID must be a number"
"Error: Task with ID 5 not found"
"Error: Task description cannot be empty"
"Error: Task description too long (max 500 characters)"
"Error: Please enter Y or N"
```

**Display Function:**
```python
def display_error(message: str) -> None:
    """
    Display error message with consistent formatting.

    Args:
        message: Error message (without "Error:" prefix)
    """
    print(f"\nError: {message}")
```

**Success Messages:**
```python
"Success: Task added with ID 1: 'Buy groceries'"
"Success: Task 1 updated to 'Buy groceries and cook dinner'"
"Success: Task 1 deleted"
"Success: Task 1 marked as complete"
"Success: Task 1 marked as incomplete"
```

### 6.4 No-Crash Guarantee

**Application must NEVER crash due to:**
- Invalid menu choice
- Invalid task ID
- Empty task list operations
- Empty or long descriptions
- Invalid confirmation input

**Guaranteed by:**
1. Input validation loops (ui.py) - ensure valid format
2. Business logic checks (operations.py) - ensure valid operations
3. Graceful error returns - no exceptions for business errors
4. Top-level exception handler (main.py) - catch unexpected errors

**Testing Requirements:**
- All error cases in specification must be tested
- Negative testing (invalid inputs) required
- Edge cases (empty list, non-existent IDs) tested

---

## 7. IMPLEMENTATION SEQUENCE

### 7.1 Build Order

**Phase 1: Foundation (Models + Operations)**
1. Create `models.py`
   - Define Task dataclass
   - Implement validation functions
   - Write unit tests

2. Create `operations.py`
   - Implement get_next_id()
   - Implement add_task()
   - Implement get_all_tasks()
   - Implement get_task_by_id()
   - Write unit tests for each function

**Phase 2: Presentation Layer**
3. Create `ui.py`
   - Implement display functions (menu, welcome, tasks)
   - Implement input functions (choice, ID, description, confirmation)
   - Implement error/success display
   - Write unit tests (with input mocking)

**Phase 3: Core Operations**
4. Complete `operations.py`
   - Implement update_task()
   - Implement delete_task()
   - Implement mark_complete()
   - Implement mark_incomplete()
   - Write unit tests for each

**Phase 4: Application Layer**
5. Create `main.py`
   - Implement main() entry point
   - Implement run_menu_loop()
   - Implement all handler functions
   - Add exception handling

**Phase 5: Integration & Testing**
6. Integration testing
   - Test complete flows (add → view → update → delete)
   - Test error handling end-to-end
   - Manual testing per specification checklist

7. Quality assurance
   - Run all unit tests (ensure ≥80% coverage)
   - Run linting (Ruff)
   - Run formatting (Black)
   - Fix any issues

### 7.2 Testing Strategy

**Unit Testing (per module):**

**test_models.py:**
- Test Task creation with valid data
- Test Task validation errors
- Test default is_complete value

**test_operations.py:**
- Test each CRUD function independently
- Mock task list data
- Test success paths
- Test error paths (invalid ID, empty description, etc.)
- Test edge cases (empty list, single task, etc.)

**test_ui.py:**
- Test display functions (capture stdout)
- Test input functions (mock stdin)
- Test validation loops
- Test error message formatting

**Integration Testing:**

**test_integration.py:**
- Test add → view flow
- Test add → update → view flow
- Test add → delete → view flow
- Test add → mark complete → view flow
- Test error recovery (invalid ID, then valid ID)

**Manual Testing:**
- Follow specification manual testing checklist (18 items)
- Test all user stories end-to-end
- Verify error messages
- Verify display formatting

---

## 8. TECHNOLOGY IMPLEMENTATION DETAILS

### 8.1 Python Version

**Required:** Python 3.11+

**Rationale:**
- Modern type hints support
- dataclass improvements
- Better error messages

**Verification:**
```python
# Add to main.py
import sys

if sys.version_info < (3, 11):
    print("Error: Python 3.11 or higher required")
    sys.exit(1)
```

### 8.2 Standard Library Usage

**Required Imports:**

```python
# models.py
from dataclasses import dataclass
from typing import Optional

# operations.py
from typing import List, Tuple, Optional
from models import Task

# ui.py
from typing import List
# Note: Does NOT import models directly

# main.py
import sys
from typing import List
from models import Task
import operations
import ui
```

**Prohibited:**
- No `pip install` packages
- No external dependencies
- No `requirements.txt` needed

### 8.3 Type Hints

**All functions must include type hints:**

```python
def add_task(tasks: List[Task], description: str) -> Tuple[bool, str, Optional[Task]]:
    """Function with full type hints."""
    pass

def display_menu() -> None:
    """Function returning nothing."""
    pass
```

**Type hint coverage:** 100% of functions

### 8.4 Code Quality Tools

**Linting:** Ruff
```bash
ruff check phase_i/
```

**Formatting:** Black
```bash
black phase_i/
```

**Type Checking (optional):** mypy
```bash
mypy phase_i/
```

### 8.5 Project Structure (Final)

```
heckathon-2/
├── CONSTITUTION.md
├── PHASE_I_SPECIFICATION.md
├── PHASE_I_PLAN.md (this document)
├── phase_i/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── operations.py
│   └── ui.py
└── tests/
    └── phase_i/
        ├── __init__.py
        ├── test_models.py
        ├── test_operations.py
        ├── test_ui.py
        └── test_integration.py
```

---

## 9. IMPLEMENTATION CONSTRAINTS

### 9.1 What Agents MUST Implement

✅ All 4 modules (main.py, models.py, operations.py, ui.py)
✅ All functions specified in PHASE_I_SPECIFICATION.md
✅ All 7 user stories (US-101 through US-107)
✅ All error handling cases
✅ Type hints on all functions
✅ Docstrings for all functions
✅ Unit tests with ≥80% coverage
✅ Integration tests for main flows

### 9.2 What Agents MUST NOT Implement

❌ File persistence
❌ Database connections
❌ Configuration files
❌ Logging frameworks
❌ Web/API interfaces
❌ Advanced features (priorities, tags, dates, categories)
❌ Multi-user support
❌ Authentication
❌ Any Phase II-V features

### 9.3 Clarification Requirements

**If agents encounter:**
- Ambiguous requirements → STOP, request clarification
- Conflicting specifications → STOP, escalate
- Missing details → STOP, request specification amendment
- Technical impossibilities → STOP, document issue

**Agents may NOT:**
- Invent features to "fill gaps"
- Make architectural decisions not in plan
- Add "improvements" or "enhancements"
- Implement partial solutions

---

## 10. TASK BREAKDOWN PREVIEW

This plan will be broken into discrete tasks in `PHASE_I_TASKS.md`:

**Estimated Task List:**
1. Task 1: Create models.py with Task dataclass
2. Task 2: Implement validation functions in models.py
3. Task 3: Write unit tests for models.py
4. Task 4: Create operations.py with get_next_id and add_task
5. Task 5: Implement get_all_tasks and get_task_by_id
6. Task 6: Write unit tests for operations.py (part 1)
7. Task 7: Implement update_task and delete_task
8. Task 8: Implement mark_complete and mark_incomplete
9. Task 9: Write unit tests for operations.py (part 2)
10. Task 10: Create ui.py with display functions
11. Task 11: Implement input functions in ui.py
12. Task 12: Write unit tests for ui.py
13. Task 13: Create main.py with entry point and menu loop
14. Task 14: Implement all handler functions in main.py
15. Task 15: Add exception handling to main.py
16. Task 16: Write integration tests
17. Task 17: Run quality checks (linting, formatting, coverage)
18. Task 18: Perform manual testing and create README

Each task will have:
- Clear acceptance criteria
- Specific deliverables
- Testing requirements
- Constitutional compliance checks

---

## 11. SUCCESS CRITERIA

This plan is considered successfully implemented when:

1. **All modules exist and are functional:**
   - main.py, models.py, operations.py, ui.py
   - All functions implemented per specification

2. **All tests pass:**
   - Unit tests ≥80% coverage
   - Integration tests pass
   - Manual testing checklist 100% complete

3. **Code quality standards met:**
   - Ruff linting passes
   - Black formatting applied
   - Type hints on all functions
   - Docstrings for all public functions

4. **Application runs correctly:**
   - Starts without errors
   - All 7 user stories work as specified
   - All error cases handled correctly
   - Exits gracefully

5. **Constitutional compliance verified:**
   - No unspecified features
   - No future-phase concepts
   - Approved technology stack only
   - Clean architecture maintained

---

## 12. RISK MITIGATION

### Risk 1: Scope Creep
**Mitigation:** Strict adherence to specification, reject any feature additions

### Risk 2: Architecture Violations
**Mitigation:** Code review against Section 5 (Separation of Responsibilities)

### Risk 3: Test Coverage Below 80%
**Mitigation:** Write tests during implementation, not after

### Risk 4: User Input Edge Cases
**Mitigation:** Comprehensive error handling testing per Section 6

### Risk 5: Performance Issues
**Mitigation:** Specification limits (1000 tasks, <100ms) guide implementation

---

## APPROVAL AND NEXT STEPS

**Plan Status:** APPROVED
**Constitutional Compliance:** VERIFIED
**Specification Compliance:** VERIFIED
**Ready for Task Breakdown:** YES

**Next Steps:**
1. Create PHASE_I_TASKS.md with discrete, actionable tasks
2. Assign tasks for implementation
3. Begin implementation per constitutional workflow

---

**END OF PHASE I TECHNICAL PLAN**

*This plan implements ONLY the requirements specified in PHASE_I_SPECIFICATION.md and is subordinate to CONSTITUTION.md. No implementation may deviate from this plan without specification amendment.*
