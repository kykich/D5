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
        """Get task statistics: count by status, avg days open, overdue count, execution times."""
        counts = self.count_by_status()
        now = datetime.now()
        total_days = 0
        days_count = 0
        overdue_count = 0
        total_execution_seconds = 0.0
        task_times = []

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

            # Execution time
            if task.done and task.completed_at:
                exec_seconds = (task.completed_at - task.created_at).total_seconds()
            else:
                exec_seconds = (now - task.created_at).total_seconds()
            total_execution_seconds += exec_seconds

            task_times.append({
                "index": len(task_times),
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "execution_seconds": exec_seconds,
                "done": task.done,
            })

        avg_days = total_days / days_count if days_count > 0 else 0.0
        avg_execution = total_execution_seconds / len(self.tasks) if self.tasks else 0.0

        return {
            "total": len(self.tasks),
            "by_status": counts,
            "avg_days_open": round(avg_days, 1),
            "overdue_count": overdue_count,
            "total_execution_seconds": total_execution_seconds,
            "avg_execution_seconds": round(avg_execution, 1),
            "task_times": task_times,
        }

    def count_by_status(self) -> Dict[str, int]:
        """Count tasks by status."""
        counts = {"todo": 0, "in_progress": 0, "done": 0}
        for task in self.tasks:
            if task.status in counts:
                counts[task.status] += 1
        return counts

    def export_html(self, filename: str) -> None:
        """Export tasks and statistics to an HTML report file."""
        stats = self.stats()
        counts = stats["by_status"]
        now = datetime.now()

        # Build task rows
        rows = ""
        for i, task in enumerate(self.tasks):
            status_class = task.status.replace("_", "-")
            priority_class = task.priority.replace("_", "-")
            due = task.due_date.strftime("%Y-%m-%d") if task.due_date else "—"
            completed = task.completed_at.strftime("%Y-%m-%d") if task.completed_at else "—"

            # Overdue check
            is_overdue = not task.done and task.due_date and task.due_date < now
            overdue_class = " overdue" if is_overdue else ""

            rows += f"""        <tr class="{status_class}">
          <td>{i}</td>
          <td>{self._html_escape(task.title)}</td>
          <td>{self._html_escape(task.description)}</td>
          <td><span class="badge status-{status_class}">{task.status}</span></td>
          <td><span class="badge priority-{priority_class}">{task.priority}</span></td>
          <td>{task.created_at.strftime("%Y-%m-%d")}</td>
          <td{overdue_class}>{due}</td>
          <td>{completed}</td>
          <td>{self._format_duration(stats["task_times"][i]["execution_seconds"])}</td>
        </tr>\n"""

        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Task Manager Report</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: #f5f7fa;
      color: #333;
      padding: 2rem;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    h1 {{ font-size: 1.8rem; margin-bottom: 1.5rem; color: #1a1a2e; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    .metric-card {{
      background: #fff;
      border-radius: 10px;
      padding: 1.2rem 1.5rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }}
    .metric-card .label {{
      font-size: 0.85rem;
      color: #888;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .metric-card .value {{
      font-size: 2rem;
      font-weight: 700;
      margin-top: 0.3rem;
    }}
    .metric-card.total .value {{ color: #4361ee; }}
    .metric-card.todo .value {{ color: #f72585; }}
    .metric-card.in_progress .value {{ color: #f77f00; }}
    .metric-card.done .value {{ color: #06d6a0; }}
    .metric-card.overdue .value {{ color: #e63946; }}
    .metric-card.avg .value {{ color: #7209b7; }}
    .metric-card.total-exec .value {{ color: #0ea5e9; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: #fff;
      border-radius: 10px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }}
    th {{
      background: #1a1a2e;
      color: #fff;
      padding: 0.8rem 1rem;
      text-align: left;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    td {{
      padding: 0.7rem 1rem;
      border-bottom: 1px solid #eee;
      font-size: 0.9rem;
    }}
    tr:last-child td {{ border-bottom: none; }}
    tr.overdue td {{ background: #fff0f0; }}
    .badge {{
      display: inline-block;
      padding: 0.2rem 0.6rem;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
    }}
    .status-todo {{ background: #fce4ec; color: #c62828; }}
    .status-in_progress {{ background: #fff3e0; color: #e65100; }}
    .status-done {{ background: #e8f5e9; color: #2e7d32; }}
    .priority-high {{ background: #ffebee; color: #c62828; }}
    .priority-medium {{ background: #fff8e1; color: #f57f17; }}
    .priority-low {{ background: #e8f5e9; color: #2e7d32; }}
    .generated {{
      text-align: right;
      font-size: 0.8rem;
      color: #999;
      margin-top: 1rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Task Manager Report</h1>

    <div class="metrics">
      <div class="metric-card total">
        <div class="label">Total</div>
        <div class="value">{stats["total"]}</div>
      </div>
      <div class="metric-card todo">
        <div class="label">To Do</div>
        <div class="value">{counts["todo"]}</div>
      </div>
      <div class="metric-card in_progress">
        <div class="label">In Progress</div>
        <div class="value">{counts["in_progress"]}</div>
      </div>
      <div class="metric-card done">
        <div class="label">Done</div>
        <div class="value">{counts["done"]}</div>
      </div>
      <div class="metric-card overdue">
        <div class="label">Overdue</div>
        <div class="value">{stats["overdue_count"]}</div>
      </div>
      <div class="metric-card avg">
        <div class="label">Avg Days Open</div>
        <div class="value">{stats["avg_days_open"]}</div>
      </div>
      <div class="metric-card total-exec">
        <div class="label">Total Execution Time</div>
        <div class="value">{self._format_duration(stats["total_execution_seconds"])}</div>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Title</th>
          <th>Description</th>
          <th>Status</th>
          <th>Priority</th>
          <th>Created</th>
          <th>Due</th>
          <th>Completed</th>
          <th>Execution Time</th>
        </tr>
      </thead>
      <tbody>
{rows}      </tbody>
    </table>

    <div class="generated">Generated: {now.strftime("%Y-%m-%d %H:%M:%S")}</div>
  </div>
</body>
</html>"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)

    @staticmethod
    def _html_escape(text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format seconds into human-readable duration."""
        if seconds < 60:
            return f"{int(seconds)}s"
        minutes = seconds / 60
        if minutes < 60:
            return f"{int(minutes)}m {int(seconds % 60)}s"
        hours = minutes / 60
        if hours < 24:
            return f"{int(hours)}h {int(minutes % 60)}m"
        days = hours / 24
        return f"{int(days)}d {int(hours % 24)}h"
