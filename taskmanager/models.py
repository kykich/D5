"""Task data models and manager."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Task:
    """Represents a single task."""

    title: str
    description: str = ""
    status: str = "todo"  # todo, in_progress, done
    priority: str = "medium"  # low, medium, high
    created_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    done: bool = False

    def mark_done(self) -> None:
        """Mark this task as done."""
        self.done = True
        self.status = "done"
        self.completed_at = datetime.now()

    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "done": self.done,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Task":
        """Create a Task from a dictionary."""
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "todo"),
            priority=data.get("priority", "medium"),
            created_at=datetime.fromisoformat(data["created_at"]),
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            done=data.get("done", False),
        )


class TaskManager:
    """Manages a collection of tasks."""

    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, title: str, description: str = "", due_date: Optional[str] = None) -> Task:
        """Add a new task and return it."""
        task = Task(title=title, description=description)
        if due_date:
            task.due_date = datetime.fromisoformat(due_date)
        self.tasks.append(task)
        return task

    def get_task(self, index: int) -> Optional[Task]:
        """Get a task by index."""
        if 0 <= index < len(self.tasks):
            return self.tasks[index]
        return None

    def complete_task(self, index: int) -> bool:
        """Mark a task as complete by index."""
        task = self.get_task(index)
        if task:
            task.mark_done()
            return True
        return False

    def delete_task(self, index: int) -> bool:
        """Delete a task by index."""
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            return True
        return False

    def list_tasks(self) -> List[Task]:
        """Return all tasks."""
        return self.tasks.copy()

    def filter_by_status(self, status: str) -> List[Task]:
        """Filter tasks by status (case-insensitive)."""
        status_lower = status.lower()
        return [t for t in self.tasks if t.status.lower() == status_lower]

    def sort_by_date(self, key: str = "due_date") -> List[Task]:
        """Sort tasks by a date field. Tasks with None are sorted to the beginning."""
        def sort_key(t):
            val = getattr(t, key)
            if val is None:
                return (0, datetime.min)
            return (1, val)
        sorted_tasks = sorted(self.tasks, key=sort_key)
        return sorted_tasks

    def search(self, query: str) -> List[Task]:
        """Search tasks by title or description (case-insensitive)."""
        query_lower = query.lower()
        return [
            t for t in self.tasks
            if query_lower in t.title.lower() or query_lower in t.description.lower()
        ]

    def filter_by_priority(self, priority: str) -> List[Task]:
        """Filter tasks by priority (case-insensitive)."""
        priority_lower = priority.lower()
        return [t for t in self.tasks if t.priority.lower() == priority_lower]

    def sort_by_priority(self) -> List[Task]:
        """Sort tasks by priority: high > medium > low."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: priority_order.get(t.priority.lower(), 1)
        )
        return sorted_tasks

    def export_csv(self, filename: str) -> None:
        """Export all tasks to a CSV file."""
        with open(filename, "w", encoding="utf-8", newline="") as f:
            f.write("index,title,description,status,priority,created_at,due_date,completed_at,done\n")
            for i, task in enumerate(self.tasks):
                due = task.due_date.strftime("%Y-%m-%d") if task.due_date else ""
                completed = task.completed_at.strftime("%Y-%m-%d") if task.completed_at else ""
                f.write(f"{i},{task.title},{task.description},{task.status},{task.priority},{task.created_at.isoformat()},{due},{completed},{task.done}\n")

    def stats(self) -> Dict[str, object]:
        """Get task statistics: count by status, avg days open, overdue count."""
        counts = self.count_by_status()
        now = datetime.now()
        total_days = 0
        days_count = 0
        overdue_count = 0

        for task in self.tasks:
            # Calculate days open
            if task.done and task.completed_at:
                days_open = (task.completed_at - task.created_at).total_seconds() / 86400
            else:
                days_open = (now - task.created_at).total_seconds() / 86400
            total_days += days_open
            days_count += 1

            # Check overdue (not done, past due date)
            if not task.done and task.due_date and task.due_date < now:
                overdue_count += 1

        avg_days = total_days / days_count if days_count > 0 else 0.0

        return {
            "total": len(self.tasks),
            "by_status": counts,
            "avg_days_open": round(avg_days, 1),
            "overdue_count": overdue_count,
        }

    def count_by_status(self) -> Dict[str, int]:
        """Count tasks by status."""
        counts = {"todo": 0, "in_progress": 0, "done": 0}
        for task in self.tasks:
            if task.status in counts:
                counts[task.status] += 1
        return counts
