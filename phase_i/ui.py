"""
CLI user interface for Phase I Todo application.

This module handles all display and input functions.
"""

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
        user_input = (
            input("Are you sure you want to delete this task? (Y/N): ")
            .strip()
            .upper()
        )

        if user_input in ["Y", "YES"]:
            return True
        elif user_input in ["N", "NO"]:
            return False
        else:
            display_error("Please enter Y or N")
