# PHASE I SPECIFICATION - FOUNDATION

**Project:** Evolution of Todo
**Phase:** I - Foundation
**Version:** 1.0
**Status:** APPROVED
**Constitutional Compliance:** Verified against CONSTITUTION.md
**Date:** 2025-12-29

---

## EXECUTIVE SUMMARY

Phase I establishes the foundational todo list application as an in-memory Python console program. This phase delivers core CRUD operations for a single user with zero persistence, focusing exclusively on basic task management functionality.

---

## CONSTITUTIONAL COMPLIANCE

This specification is created under:
- **Article I:** Spec-Driven Development Mandate
- **Article III:** Phase Governance (Section 3.1 - Phase Scope Boundaries)
- **Article IV:** Technology Constraints (Section 4.1 - Python backend)
- **Article VIII:** Phase-Specific Provisions (Section 8.1 - Phase I)

All implementation must follow: Constitution → This Spec → Plan → Tasks → Code

---

## PHASE I SCOPE

### In Scope
- In-memory data storage (Python list/dict structures)
- Console-based menu interface
- Single user operation
- Basic CRUD operations
- Task completion status tracking
- Input validation and error handling

### Explicitly Out of Scope
- File persistence
- Database integration
- Multi-user support
- Authentication or authorization
- Web interface or REST API
- Advanced features (priorities, tags, due dates, etc.)
- Agent or AI integration
- Configuration files
- Logging beyond console output
- Any Phase II-V features

---

## USER STORIES

### US-101: Add Task
**As a** user
**I want to** add a new task with a description
**So that** I can track things I need to do

**Acceptance Criteria:**
- System prompts for task description
- Task description must be non-empty (1-500 characters)
- Task is assigned a unique numeric ID (auto-incrementing)
- Task is created with status "incomplete" by default
- Task is added to the in-memory task list
- System confirms task was added with ID and description
- User returns to main menu

**Error Cases:**
- Empty description: Display "Error: Task description cannot be empty"
- Description >500 chars: Display "Error: Task description too long (max 500 characters)"

---

### US-102: View Task List
**As a** user
**I want to** view all my tasks
**So that** I can see what needs to be done

**Acceptance Criteria:**
- System displays all tasks in a formatted list
- Each task shows: ID, Status (✓ or ✗), Description
- Tasks are ordered by ID (oldest first)
- Completed tasks are clearly marked
- Display shows total count of tasks
- User returns to main menu

**Error Cases:**
- Empty list: Display "No tasks found. Add a task to get started."

**Display Format:**
```
Your Tasks (3 total):
----------------------------------------
ID: 1 | Status: ✗ | Buy groceries
ID: 2 | Status: ✓ | Finish homework
ID: 3 | Status: ✗ | Call dentist
----------------------------------------
```

---

### US-103: Update Task
**As a** user
**I want to** update a task's description
**So that** I can correct or modify task details

**Acceptance Criteria:**
- System prompts for task ID
- System validates task ID exists
- System displays current task description
- System prompts for new description
- New description must be non-empty (1-500 characters)
- Task description is updated in memory
- System confirms update with new description
- User returns to main menu

**Error Cases:**
- Invalid ID format: Display "Error: Task ID must be a number"
- Non-existent ID: Display "Error: Task with ID {id} not found"
- Empty new description: Display "Error: Task description cannot be empty"
- Description >500 chars: Display "Error: Task description too long (max 500 characters)"

---

### US-104: Delete Task
**As a** user
**I want to** delete a task
**So that** I can remove tasks I no longer need

**Acceptance Criteria:**
- System prompts for task ID
- System validates task ID exists
- System displays task to be deleted
- System asks for confirmation (Y/N)
- If confirmed, task is removed from in-memory list
- System confirms deletion
- User returns to main menu

**Error Cases:**
- Invalid ID format: Display "Error: Task ID must be a number"
- Non-existent ID: Display "Error: Task with ID {id} not found"
- Invalid confirmation input: Display "Error: Please enter Y or N"

---

### US-105: Mark Task Complete
**As a** user
**I want to** mark a task as complete
**So that** I can track my progress

**Acceptance Criteria:**
- System prompts for task ID
- System validates task ID exists
- Task status is updated to "complete"
- System confirms task marked complete
- User returns to main menu

**Error Cases:**
- Invalid ID format: Display "Error: Task ID must be a number"
- Non-existent ID: Display "Error: Task with ID {id} not found"
- Already complete: Display "Info: Task {id} is already marked complete"

---

### US-106: Mark Task Incomplete
**As a** user
**I want to** mark a task as incomplete
**So that** I can reopen tasks if needed

**Acceptance Criteria:**
- System prompts for task ID
- System validates task ID exists
- Task status is updated to "incomplete"
- System confirms task marked incomplete
- User returns to main menu

**Error Cases:**
- Invalid ID format: Display "Error: Task ID must be a number"
- Non-existent ID: Display "Error: Task with ID {id} not found"
- Already incomplete: Display "Info: Task {id} is already marked incomplete"

---

### US-107: Exit Application
**As a** user
**I want to** exit the application
**So that** I can stop using the program

**Acceptance Criteria:**
- System displays goodbye message
- Application terminates gracefully
- No errors or exceptions on exit

---

## DATA MODEL

### Task Entity

```python
Task {
    id: int              # Unique identifier, auto-incrementing, starts at 1
    description: str     # Task description, 1-500 characters
    is_complete: bool    # Completion status, default False
}
```

**Field Constraints:**
- `id`: Positive integer, unique, auto-generated, immutable
- `description`: Non-empty string, 1-500 characters, required
- `is_complete`: Boolean, required, default `False`

**In-Memory Storage:**
- Tasks stored in Python list: `List[Task]`
- ID generation via counter: `next_id = len(tasks) + 1`
- Task lookup by ID via list iteration or dictionary mapping

**Data Structure Options:**
```python
# Option 1: List of dictionaries
tasks = [
    {"id": 1, "description": "Buy groceries", "is_complete": False},
    {"id": 2, "description": "Finish homework", "is_complete": True}
]

# Option 2: List of Task objects (if using dataclass/class)
@dataclass
class Task:
    id: int
    description: str
    is_complete: bool = False

tasks = [Task(...), Task(...)]
```

**Implementation Note:** Either option is acceptable; choose based on simplicity and maintainability.

---

## CLI INTERACTION FLOW

### Application Start
```
========================================
    WELCOME TO TODO LIST MANAGER
========================================
```

### Main Menu
```
========================================
           MAIN MENU
========================================
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete
6. Mark Task Incomplete
7. Exit
========================================
Enter your choice (1-7): _
```

### Menu Selection Flow
1. Display main menu
2. Prompt for user input (1-7)
3. Validate input is numeric and in range
4. Execute corresponding feature
5. Return to main menu (except Exit)

**Invalid Menu Input:**
```
Error: Invalid choice. Please enter a number between 1 and 7.
```

---

## FEATURE INTERACTION FLOWS

### 1. Add Task Flow
```
Enter your choice (1-7): 1

--- Add New Task ---
Enter task description: Buy groceries

Success: Task added with ID 1: "Buy groceries"
Press Enter to continue...

[Return to Main Menu]
```

### 2. View Tasks Flow
```
Enter your choice (1-7): 2

--- Your Task List ---
Your Tasks (2 total):
----------------------------------------
ID: 1 | Status: ✗ | Buy groceries
ID: 2 | Status: ✓ | Finish homework
----------------------------------------
Press Enter to continue...

[Return to Main Menu]
```

### 3. Update Task Flow
```
Enter your choice (1-7): 3

--- Update Task ---
Enter task ID to update: 1

Current task: "Buy groceries"
Enter new description: Buy groceries and cook dinner

Success: Task 1 updated to "Buy groceries and cook dinner"
Press Enter to continue...

[Return to Main Menu]
```

### 4. Delete Task Flow
```
Enter your choice (1-7): 4

--- Delete Task ---
Enter task ID to delete: 1

Task to delete: ID 1 - "Buy groceries"
Are you sure you want to delete this task? (Y/N): Y

Success: Task 1 deleted
Press Enter to continue...

[Return to Main Menu]
```

### 5. Mark Complete Flow
```
Enter your choice (1-7): 5

--- Mark Task Complete ---
Enter task ID to mark complete: 1

Success: Task 1 marked as complete
Press Enter to continue...

[Return to Main Menu]
```

### 6. Mark Incomplete Flow
```
Enter your choice (1-7): 6

--- Mark Task Incomplete ---
Enter task ID to mark incomplete: 1

Success: Task 1 marked as incomplete
Press Enter to continue...

[Return to Main Menu]
```

### 7. Exit Flow
```
Enter your choice (1-7): 7

========================================
Thank you for using Todo List Manager!
Goodbye!
========================================

[Application terminates]
```

---

## ERROR HANDLING

### Input Validation Rules

**Menu Choice:**
- Must be numeric
- Must be 1-7
- Non-numeric: "Error: Invalid choice. Please enter a number between 1 and 7."
- Out of range: "Error: Invalid choice. Please enter a number between 1 and 7."

**Task ID:**
- Must be numeric integer
- Must exist in task list
- Non-numeric: "Error: Task ID must be a number"
- Non-existent: "Error: Task with ID {id} not found"

**Task Description:**
- Must not be empty (after stripping whitespace)
- Must be ≤500 characters
- Empty: "Error: Task description cannot be empty"
- Too long: "Error: Task description too long (max 500 characters)"

**Confirmation (Y/N):**
- Must be 'Y', 'y', 'N', or 'n'
- Case-insensitive
- Invalid: "Error: Please enter Y or N"

### Error Display Format
```
Error: [Clear description of the error]
Press Enter to continue...
[Return to appropriate menu/prompt]
```

### Exception Handling
- Catch keyboard interrupt (Ctrl+C): Display "Application interrupted by user" and exit gracefully
- Catch unexpected errors: Display "An unexpected error occurred. Please restart the application." and exit

---

## ACCEPTANCE CRITERIA

### Phase I Complete When:
1. ✅ All 7 user stories are implemented
2. ✅ All acceptance criteria for each user story pass
3. ✅ All error cases are handled correctly
4. ✅ Menu system functions without crashes
5. ✅ Task data persists in memory during runtime
6. ✅ Application starts and exits cleanly
7. ✅ Code follows clean architecture principles (Article V)
8. ✅ Code includes type hints and passes linting
9. ✅ Unit tests achieve ≥80% coverage
10. ✅ Manual testing confirms all flows work correctly

### Quality Gates
- No hardcoded values that should be configurable
- No commented-out code
- No placeholder or TODO comments
- All functions have docstrings
- Code passes Ruff linting
- Code formatted with Black

---

## TECHNOLOGY REQUIREMENTS

Per Constitutional Article IV:

**Language:** Python 3.11+

**Required Standard Libraries Only:**
- `typing` - For type hints
- `dataclasses` - For Task model (optional)
- `sys` - For exit handling

**Prohibited:**
- No external dependencies
- No pip packages
- No database libraries
- No web frameworks
- No file I/O libraries

**Project Structure:**
```
heckathon-2/
├── CONSTITUTION.md
├── PHASE_I_SPECIFICATION.md
├── phase_i/
│   ├── __init__.py
│   ├── main.py           # Entry point, menu system
│   ├── models.py         # Task data model
│   ├── operations.py     # CRUD operations
│   └── ui.py             # CLI display functions
└── tests/
    └── phase_i/
        ├── __init__.py
        ├── test_models.py
        ├── test_operations.py
        └── test_ui.py
```

---

## ARCHITECTURE REQUIREMENTS

Per Constitutional Article V (Clean Architecture):

### Layer Separation

**1. Presentation Layer (ui.py):**
- Display menus
- Capture user input
- Format output
- Handle display logic only
- No business logic

**2. Business Logic Layer (operations.py):**
- Implement CRUD operations
- Validate business rules
- Coordinate task operations
- Return success/error states
- No direct user interaction

**3. Domain Model Layer (models.py):**
- Define Task entity
- Enforce data constraints
- Pure data structures
- No external dependencies

**4. Application Layer (main.py):**
- Application entry point
- Menu loop coordination
- Connect UI to operations
- Handle application lifecycle

### Dependencies
```
main.py → ui.py → operations.py → models.py
(outer) ←―――――――――――――――――――――――――― (inner)
```

- Outer layers depend on inner layers
- Inner layers have no knowledge of outer layers
- No circular dependencies

### Function Responsibilities

**models.py:**
```python
Task: Dataclass or class defining task structure
validate_description(desc: str) -> bool
create_task(id: int, description: str) -> Task
```

**operations.py:**
```python
add_task(tasks: List[Task], description: str) -> Tuple[bool, str, Optional[Task]]
get_all_tasks(tasks: List[Task]) -> List[Task]
get_task_by_id(tasks: List[Task], task_id: int) -> Optional[Task]
update_task(tasks: List[Task], task_id: int, new_desc: str) -> Tuple[bool, str]
delete_task(tasks: List[Task], task_id: int) -> Tuple[bool, str]
mark_complete(tasks: List[Task], task_id: int) -> Tuple[bool, str]
mark_incomplete(tasks: List[Task], task_id: int) -> Tuple[bool, str]
get_next_id(tasks: List[Task]) -> int
```

**ui.py:**
```python
display_welcome() -> None
display_menu() -> None
get_menu_choice() -> int
display_tasks(tasks: List[Task]) -> None
get_task_description() -> str
get_task_id() -> int
get_confirmation() -> bool
display_success(message: str) -> None
display_error(message: str) -> None
pause() -> None
```

**main.py:**
```python
main() -> None
run_menu_loop(tasks: List[Task]) -> None
handle_add_task(tasks: List[Task]) -> None
handle_view_tasks(tasks: List[Task]) -> None
handle_update_task(tasks: List[Task]) -> None
handle_delete_task(tasks: List[Task]) -> None
handle_mark_complete(tasks: List[Task]) -> None
handle_mark_incomplete(tasks: List[Task]) -> None
```

---

## TESTING REQUIREMENTS

Per Constitutional Article V, Section 5.5:

### Unit Tests (≥80% coverage)

**test_models.py:**
- Test Task creation
- Test field validation
- Test default values

**test_operations.py:**
- Test add_task with valid/invalid input
- Test get_all_tasks with empty/populated list
- Test get_task_by_id with valid/invalid ID
- Test update_task with valid/invalid input
- Test delete_task with valid/invalid ID
- Test mark_complete with valid/invalid ID
- Test mark_incomplete with valid/invalid ID
- Test get_next_id with empty/populated list

**test_ui.py:**
- Test display functions (output verification)
- Test input validation functions
- Test error message formatting

### Integration Tests

**test_integration.py:**
- Test complete add → view → update → delete flow
- Test complete add → mark complete → view flow
- Test error recovery flows
- Test menu navigation

### Manual Testing Checklist
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

---

## NON-FUNCTIONAL REQUIREMENTS

### Performance
- Menu response: Instant (<100ms)
- Task operations: Instant for lists up to 1000 tasks
- Memory: <10MB for 1000 tasks

### Usability
- Clear error messages
- Consistent formatting
- Intuitive menu flow
- Visual separation between sections

### Maintainability
- Type hints on all functions
- Docstrings for all public functions
- Clear variable names
- Separated concerns
- No code duplication

### Reliability
- No crashes on invalid input
- Graceful error handling
- Clean application termination

---

## IMPLEMENTATION CONSTRAINTS

### What Agents MUST Do
1. Implement exactly these 7 features (US-101 through US-107)
2. Follow the specified CLI interaction flows exactly
3. Use the defined data model structure
4. Implement all error cases as specified
5. Follow the layered architecture pattern
6. Write tests achieving ≥80% coverage
7. Use only Python standard library
8. Include type hints and docstrings

### What Agents MUST NOT Do
1. Add features not in this specification
2. Implement persistence (files, databases)
3. Add advanced features (priorities, tags, dates, etc.)
4. Create web or API interfaces
5. Add configuration files
6. Implement logging frameworks
7. Add any Phase II-V concepts
8. Invent "improvements" or "enhancements"

### Clarification Protocol
If ambiguity exists:
1. STOP implementation
2. Document the ambiguity
3. Request specification clarification
4. Wait for specification amendment
5. Resume only after clarification

---

## DELIVERABLES

### Code Deliverables
1. `phase_i/main.py` - Application entry point
2. `phase_i/models.py` - Task data model
3. `phase_i/operations.py` - Business logic
4. `phase_i/ui.py` - CLI interface
5. `tests/phase_i/*` - Test suite

### Documentation Deliverables
1. `PHASE_I_PLAN.md` - Implementation plan (to be created)
2. `PHASE_I_TASKS.md` - Task breakdown (to be created)
3. `README_PHASE_I.md` - User instructions (to be created after implementation)

### Validation Deliverables
1. Test execution report (all tests passing)
2. Coverage report (≥80%)
3. Linting report (no errors)
4. Manual testing checklist (all items checked)

---

## SUCCESS CRITERIA

Phase I is considered COMPLETE and SUCCESSFUL when:

1. **Functional Completeness:**
   - All 7 user stories implemented
   - All acceptance criteria met
   - All error cases handled

2. **Quality Standards:**
   - Code passes all tests (≥80% coverage)
   - Code passes linting (Ruff)
   - Code formatted (Black)
   - All functions have type hints and docstrings

3. **Architectural Compliance:**
   - Clean architecture layers respected
   - No circular dependencies
   - Clear separation of concerns

4. **Constitutional Compliance:**
   - Follows spec-driven development
   - No unspecified features
   - Uses approved technologies
   - Stays within phase boundaries

5. **User Acceptance:**
   - Manual testing checklist 100% complete
   - Application runs without crashes
   - All features work as specified

---

## PHASE I COMPLETION CHECKLIST

- [ ] PHASE_I_PLAN.md created and approved
- [ ] PHASE_I_TASKS.md created with all tasks defined
- [ ] All tasks implemented
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Test coverage ≥80%
- [ ] Ruff linting passes with no errors
- [ ] Black formatting applied
- [ ] Manual testing checklist 100% complete
- [ ] README_PHASE_I.md created
- [ ] Constitutional compliance verified
- [ ] Code review completed
- [ ] Phase I APPROVED for production

---

## APPROVAL

**Specification Status:** APPROVED
**Constitutional Compliance:** VERIFIED
**Ready for Planning:** YES

**Next Steps:**
1. Create PHASE_I_PLAN.md (implementation plan)
2. Create PHASE_I_TASKS.md (task breakdown)
3. Begin implementation per constitutional workflow

---

**END OF PHASE I SPECIFICATION**

*This specification is subordinate to CONSTITUTION.md and may only be amended through the constitutional amendment process defined in Article VI, Section 6.3.*
