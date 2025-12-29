"""
Main application entry point for Phase I Todo application.

This module orchestrates the menu loop and connects UI to operations.
"""

import sys
from typing import List
from phase_i.models import Task
from phase_i import ui
from phase_i import operations


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


if __name__ == "__main__":
    main()
