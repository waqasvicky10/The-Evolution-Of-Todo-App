"""
Unit tests for UI module.

Tests display and input functions using stdout/stdin mocking.
"""

import pytest
from unittest.mock import patch
from phase_i import ui
from phase_i.models import Task


# ============================================================================
# Display function tests
# ============================================================================


def test_display_welcome(capsys):
    """Test welcome banner output."""
    ui.display_welcome()
    captured = capsys.readouterr()
    assert "WELCOME TO TODO LIST MANAGER" in captured.out
    assert "=" * 40 in captured.out


def test_display_menu(capsys):
    """Test menu displays all 7 options."""
    ui.display_menu()
    captured = capsys.readouterr()
    assert "MAIN MENU" in captured.out
    assert "1. Add Task" in captured.out
    assert "2. View Tasks" in captured.out
    assert "3. Update Task" in captured.out
    assert "4. Delete Task" in captured.out
    assert "5. Mark Task Complete" in captured.out
    assert "6. Mark Task Incomplete" in captured.out
    assert "7. Exit" in captured.out


def test_display_tasks_empty(capsys):
    """Test displaying empty task list."""
    tasks = []
    ui.display_tasks(tasks)
    captured = capsys.readouterr()
    assert "No tasks found" in captured.out


def test_display_tasks_single(capsys):
    """Test displaying single task."""
    tasks = [Task(1, "Buy groceries", False)]
    ui.display_tasks(tasks)
    captured = capsys.readouterr()
    assert "Your Tasks (1 total)" in captured.out
    assert "ID: 1" in captured.out
    assert "Buy groceries" in captured.out


def test_display_tasks_multiple(capsys):
    """Test displaying multiple tasks."""
    tasks = [
        Task(1, "Buy groceries", False),
        Task(2, "Finish homework", True),
    ]
    ui.display_tasks(tasks)
    captured = capsys.readouterr()
    assert "Your Tasks (2 total)" in captured.out
    assert "ID: 1" in captured.out
    assert "Buy groceries" in captured.out
    assert "ID: 2" in captured.out
    assert "Finish homework" in captured.out


def test_display_tasks_complete_status(capsys):
    """Test displaying complete task shows checkmark."""
    tasks = [Task(1, "Completed task", True)]
    ui.display_tasks(tasks)
    captured = capsys.readouterr()
    assert "✓" in captured.out


def test_display_tasks_incomplete_status(capsys):
    """Test displaying incomplete task shows X."""
    tasks = [Task(1, "Incomplete task", False)]
    ui.display_tasks(tasks)
    captured = capsys.readouterr()
    assert "✗" in captured.out


def test_display_error(capsys):
    """Test error message formatting."""
    ui.display_error("Test error message")
    captured = capsys.readouterr()
    assert "Error: Test error message" in captured.out


def test_display_success(capsys):
    """Test success message formatting."""
    ui.display_success("Test success message")
    captured = capsys.readouterr()
    assert "Success: Test success message" in captured.out


def test_display_goodbye(capsys):
    """Test goodbye banner output."""
    ui.display_goodbye()
    captured = capsys.readouterr()
    assert "Thank you for using Todo List Manager!" in captured.out
    assert "Goodbye!" in captured.out


# ============================================================================
# Input function tests
# ============================================================================


@patch("builtins.input", side_effect=["3"])
def test_get_menu_choice_valid(mock_input):
    """Test getting valid menu choice."""
    choice = ui.get_menu_choice()
    assert choice == 3


@patch("builtins.input", side_effect=["abc", "10", "5"])
def test_get_menu_choice_invalid_then_valid(mock_input, capsys):
    """Test get_menu_choice loops on error."""
    choice = ui.get_menu_choice()
    assert choice == 5
    captured = capsys.readouterr()
    assert "Error:" in captured.out


@patch("builtins.input", side_effect=["0", "8", "1"])
def test_get_menu_choice_out_of_range(mock_input, capsys):
    """Test get_menu_choice rejects out of range values."""
    choice = ui.get_menu_choice()
    assert choice == 1
    captured = capsys.readouterr()
    assert captured.out.count("Error:") == 2


@patch("builtins.input", side_effect=["42"])
def test_get_task_id_valid(mock_input):
    """Test getting valid task ID."""
    task_id = ui.get_task_id()
    assert task_id == 42


@patch("builtins.input", side_effect=["abc", "5"])
def test_get_task_id_invalid_then_valid(mock_input, capsys):
    """Test get_task_id loops on non-numeric."""
    task_id = ui.get_task_id()
    assert task_id == 5
    captured = capsys.readouterr()
    assert "Task ID must be a number" in captured.out


@patch("builtins.input", side_effect=["Buy groceries"])
def test_get_task_description_valid(mock_input):
    """Test getting valid task description."""
    description = ui.get_task_description()
    assert description == "Buy groceries"


@patch("builtins.input", side_effect=["", "Valid description"])
def test_get_task_description_empty_then_valid(mock_input, capsys):
    """Test get_task_description loops on empty."""
    description = ui.get_task_description()
    assert description == "Valid description"
    captured = capsys.readouterr()
    assert "Task description cannot be empty" in captured.out


@patch("builtins.input", side_effect=["a" * 501, "Valid"])
def test_get_task_description_too_long(mock_input, capsys):
    """Test get_task_description rejects >500 chars."""
    description = ui.get_task_description()
    assert description == "Valid"
    captured = capsys.readouterr()
    assert "Task description too long" in captured.out


@patch("builtins.input", side_effect=["  Trimmed  "])
def test_get_task_description_strips_whitespace(mock_input):
    """Test get_task_description strips whitespace."""
    description = ui.get_task_description()
    assert description == "Trimmed"


@patch("builtins.input", side_effect=["Y"])
def test_get_confirmation_yes(mock_input):
    """Test get_confirmation returns True for 'Y'."""
    result = ui.get_confirmation()
    assert result is True


@patch("builtins.input", side_effect=["N"])
def test_get_confirmation_no(mock_input):
    """Test get_confirmation returns False for 'N'."""
    result = ui.get_confirmation()
    assert result is False


@patch("builtins.input", side_effect=["yes"])
def test_get_confirmation_yes_lowercase(mock_input):
    """Test get_confirmation accepts 'yes' (case-insensitive)."""
    result = ui.get_confirmation()
    assert result is True


@patch("builtins.input", side_effect=["NO"])
def test_get_confirmation_no_uppercase(mock_input):
    """Test get_confirmation accepts 'NO'."""
    result = ui.get_confirmation()
    assert result is False


@patch("builtins.input", side_effect=["maybe", "Y"])
def test_get_confirmation_invalid_then_valid(mock_input, capsys):
    """Test get_confirmation loops on invalid input."""
    result = ui.get_confirmation()
    assert result is True
    captured = capsys.readouterr()
    assert "Please enter Y or N" in captured.out
