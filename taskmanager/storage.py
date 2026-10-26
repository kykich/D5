"""JSON file storage for tasks."""

import json
import os
from typing import List, Optional

from .models import Task


STORAGE_FILE = "tasks_data.json"


def save_tasks(tasks: List[Task], filepath: Optional[str] = None) -> None:
    """Save tasks to a JSON file."""
    if filepath is None:
        filepath = STORAGE_FILE
    data = [task.to_dict() for task in tasks]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_tasks(filepath: Optional[str] = None) -> List[Task]:
    """Load tasks from a JSON file."""
    if filepath is None:
        filepath = STORAGE_FILE
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Task.from_dict(item) for item in data]


def append_task(task_dict: dict, filepath: Optional[str] = None) -> None:
    """Append a single task to the JSON file."""
    if filepath is None:
        filepath = STORAGE_FILE
    existing = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            existing = json.load(f)
    existing.append(task_dict)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
