"""Utility functions for validation and common operations."""

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import TaskManager


VALID_STATUSES = ["todo", "in_progress", "done"]
VALID_PRIORITIES = ["low", "medium", "high"]


def validate_task_index(index_str: str) -> int:
    """Validate that input is a valid integer index.

    Args:
        index_str: String representation of the index.

    Returns:
        Validated integer index.

    Exits:
        System exit with error message if invalid.
    """
    try:
        index = int(index_str)
        if index < 0:
            raise ValueError
        return index
    except ValueError:
        print(f"Error: Invalid index '{index_str}'. Must be a non-negative integer.")
        sys.exit(1)


def validate_status(status: str) -> str:
    """Validate that status is one of the allowed values.

    Args:
        status: Status string to validate.

    Returns:
        Validated status string.

    Exits:
        System exit with error message if invalid.
    """
    if status not in VALID_STATUSES:
        print(f"Error: Invalid status '{status}'. Must be one of: {', '.join(VALID_STATUSES)}")
        sys.exit(1)
    return status


def validate_priority(priority: str) -> str:
    """Validate that priority is one of the allowed values.

    Args:
        priority: Priority string to validate.

    Returns:
        Validated priority string.

    Exits:
        System exit with error message if invalid.
    """
    if priority.lower() not in VALID_PRIORITIES:
        print(f"Error: Invalid priority '{priority}'. Must be one of: {', '.join(VALID_PRIORITIES)}")
        sys.exit(1)
    return priority.lower()


def check_task_exists(manager: "TaskManager", index: int) -> bool:
    """Check if a task exists at the given index.

    Args:
        manager: TaskManager instance.
        index: Task index to check.

    Returns:
        True if task exists, False otherwise.
    """
    if index >= len(manager.tasks):
        print(f"Error: No task at index {index}. Total tasks: {len(manager.tasks)}")
        return False
    return True
