"""Unit tests for taskmanager.models."""

import pytest
from datetime import datetime, timedelta

from taskmanager.models import Task, TaskManager


class TestTask:
    """Tests for the Task dataclass."""

    def test_create_task_default_values(self):
        """Test creating a task with default values."""
        task = Task(title="Test Task")
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.status == "todo"
        assert task.priority == "medium"
        assert task.done is False
        assert task.completed_at is None

    def test_create_task_with_values(self):
        """Test creating a task with custom values."""
        due = datetime.now() + timedelta(days=7)
        task = Task(
            title="Test Task",
            description="A test task",
            status="in_progress",
            priority="high",
            due_date=due,
        )
        assert task.title == "Test Task"
        assert task.description == "A test task"
        assert task.status == "in_progress"
        assert task.priority == "high"
        assert task.due_date == due

    def test_mark_done_sets_completed_at(self):
        """Test that mark_done sets completed_at timestamp."""
        task = Task(title="Test Task")
        assert task.completed_at is None
        task.mark_done()
        assert task.done is True
        assert task.status == "done"
        assert task.completed_at is not None
        assert isinstance(task.completed_at, datetime)

    def test_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(title="Test", description="Desc", priority="high")
        task.mark_done()
        d = task.to_dict()
        assert d["title"] == "Test"
        assert d["description"] == "Desc"
        assert d["status"] == "done"
        assert d["priority"] == "high"
        assert d["done"] is True
        assert d["completed_at"] is not None

    def test_from_dict(self):
        """Test creating task from dictionary."""
        data = {
            "title": "Test",
            "description": "Desc",
            "status": "in_progress",
            "priority": "low",
            "created_at": datetime.now().isoformat(),
            "due_date": None,
            "completed_at": None,
            "done": False,
        }
        task = Task.from_dict(data)
        assert task.title == "Test"
        assert task.description == "Desc"
        assert task.status == "in_progress"
        assert task.priority == "low"
        assert task.done is False

    def test_from_dict_with_due_date(self):
        """Test from_dict with a due date."""
        due = datetime.now().isoformat()
        data = {
            "title": "Test",
            "description": "",
            "status": "todo",
            "priority": "medium",
            "created_at": datetime.now().isoformat(),
            "due_date": due,
            "completed_at": None,
            "done": False,
        }
        task = Task.from_dict(data)
        assert task.due_date is not None


class TestTaskManager:
    """Tests for the TaskManager class."""

    def test_add_task(self):
        """Test adding a task."""
        tm = TaskManager()
        task = tm.add_task("New Task", "Description")
        assert len(tm.tasks) == 1
        assert tm.tasks[0].title == "New Task"
        assert tm.tasks[0].description == "Description"

    def test_add_task_with_due_date(self):
        """Test adding a task with due date."""
        tm = TaskManager()
        due = "2025-12-31T23:59:59"
        task = tm.add_task("Task", due_date=due)
        assert task.due_date is not None

    def test_get_task_valid_index(self):
        """Test getting a task by valid index."""
        tm = TaskManager()
        tm.add_task("Task 1")
        tm.add_task("Task 2")
        task = tm.get_task(1)
        assert task is not None
        assert task.title == "Task 2"

    def test_get_task_invalid_index(self):
        """Test getting a task by invalid index."""
        tm = TaskManager()
        tm.add_task("Task 1")
        assert tm.get_task(5) is None

    def test_complete_task(self):
        """Test completing a task."""
        tm = TaskManager()
        tm.add_task("Task 1")
        result = tm.complete_task(0)
        assert result is True
        assert tm.tasks[0].done is True
        assert tm.tasks[0].status == "done"
        assert tm.tasks[0].completed_at is not None

    def test_complete_task_invalid_index(self):
        """Test completing a task with invalid index."""
        tm = TaskManager()
        tm.add_task("Task 1")
        result = tm.complete_task(5)
        assert result is False

    def test_delete_task(self):
        """Test deleting a task."""
        tm = TaskManager()
        tm.add_task("Task 1")
        tm.add_task("Task 2")
        result = tm.delete_task(0)
        assert result is True
        assert len(tm.tasks) == 1
        assert tm.tasks[0].title == "Task 2"

    def test_delete_task_invalid_index(self):
        """Test deleting a task with invalid index."""
        tm = TaskManager()
        tm.add_task("Task 1")
        result = tm.delete_task(5)
        assert result is False

    def test_list_tasks(self):
        """Test listing all tasks."""
        tm = TaskManager()
        tm.add_task("Task 1")
        tm.add_task("Task 2")
        tasks = tm.list_tasks()
        assert len(tasks) == 2
        assert tasks is not tm.tasks  # Should be a copy

    def test_filter_by_status_case_insensitive(self):
        """Test filtering by status is case-insensitive."""
        tm = TaskManager()
        tm.add_task("Task 1").status = "Done"
        tm.add_task("Task 2").status = "todo"
        tm.add_task("Task 3").status = "DONE"
        results = tm.filter_by_status("done")
        assert len(results) == 2

    def test_sort_by_date_with_none(self):
        """Test sorting by date handles None values."""
        tm = TaskManager()
        tm.add_task("Task 1")  # No due_date
        tm.add_task("Task 2", due_date="2025-12-31")
        tm.add_task("Task 3")  # No due_date
        sorted_tasks = tm.sort_by_date("due_date")
        # Tasks with None should be first
        assert sorted_tasks[0].title == "Task 1"

    def test_search(self):
        """Test searching tasks."""
        tm = TaskManager()
        tm.add_task("Buy groceries", "Milk and eggs")
        tm.add_task("Walk the dog")
        results = tm.search("groceries")
        assert len(results) == 1
        assert results[0].title == "Buy groceries"

    def test_search_case_insensitive(self):
        """Test searching is case-insensitive."""
        tm = TaskManager()
        tm.add_task("Buy Groceries")
        results = tm.search("groceries")
        assert len(results) == 1

    def test_filter_by_priority(self):
        """Test filtering by priority."""
        tm = TaskManager()
        tm.add_task("Task 1").priority = "high"
        tm.add_task("Task 2").priority = "low"
        tm.add_task("Task 3").priority = "high"
        results = tm.filter_by_priority("high")
        assert len(results) == 2

    def test_sort_by_priority(self):
        """Test sorting by priority."""
        tm = TaskManager()
        tm.add_task("Low").priority = "low"
        tm.add_task("High").priority = "high"
        tm.add_task("Medium").priority = "medium"
        sorted_tasks = tm.sort_by_priority()
        assert sorted_tasks[0].priority == "high"
        assert sorted_tasks[1].priority == "medium"
        assert sorted_tasks[2].priority == "low"

    def test_count_by_status(self):
        """Test counting tasks by status."""
        tm = TaskManager()
        tm.add_task("Task 1")
        tm.add_task("Task 2")
        tm.add_task("Task 3").status = "done"
        counts = tm.count_by_status()
        assert counts["todo"] == 2
        assert counts["done"] == 1

    def test_stats(self):
        """Test stats method."""
        tm = TaskManager()
        tm.add_task("Task 1")
        tm.add_task("Task 2")
        stats = tm.stats()
        assert stats["total"] == 2
        assert "avg_days_open" in stats
        assert "overdue_count" in stats

    def test_export_html(self, tmp_path):
        """Test exporting tasks to HTML."""
        tm = TaskManager()
        tm.add_task("Task 1", "Description 1")
        tm.add_task("Task 2", "Description 2")
        tm.tasks[0].status = "done"
        tm.tasks[0].mark_done()

        html_file = tmp_path / "report.html"
        tm.export_html(str(html_file))

        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "Task 1" in content
        assert "Task 2" in content
        assert "Description 1" in content
        assert "Done</div>" in content or "done" in content.lower()
        assert "Generated:" in content
        assert "Execution Time" in content
        assert "Total Execution Time" in content

    def test_export_html_empty(self, tmp_path):
        """Test exporting empty task list to HTML."""
        tm = TaskManager()
        html_file = tmp_path / "report.html"
        tm.export_html(str(html_file))

        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "Total</div>\n        <div class=\"value\">0</div>" in content

    def test_export_html_contains_metrics(self, tmp_path):
        """Test HTML report contains all metric cards."""
        tm = TaskManager()
        tm.add_task("Task 1")
        tm.add_task("Task 2")
        tm.add_task("Task 3").status = "done"
        tm.tasks[2].mark_done()

        html_file = tmp_path / "report.html"
        tm.export_html(str(html_file))

        content = html_file.read_text(encoding="utf-8")
        assert "Total" in content
        assert "To Do" in content
        assert "In Progress" in content
        assert "Done</div>" in content or "Done" in content
        assert "Overdue" in content
        assert "Avg Days Open" in content
        assert "Total Execution Time" in content

    def test_html_escape(self):
        """Test HTML escaping of special characters."""
        assert TaskManager._html_escape("<script>") == "&lt;script&gt;"
        assert TaskManager._html_escape('a "quote"') == 'a &quot;quote&quot;'
        assert TaskManager._html_escape("a & b") == "a &amp; b"
        assert TaskManager._html_escape("normal") == "normal"

    def test_format_duration_seconds(self):
        """Test formatting duration in seconds."""
        assert TaskManager._format_duration(12.5) == "12s"
        assert TaskManager._format_duration(0) == "0s"
        assert TaskManager._format_duration(59.9) == "59s"

    def test_format_duration_minutes(self):
        """Test formatting duration in minutes."""
        assert TaskManager._format_duration(45 * 60) == "45m 0s"
        assert TaskManager._format_duration(45 * 60 + 30) == "45m 30s"
        assert TaskManager._format_duration(59 * 60 + 59) == "59m 59s"

    def test_format_duration_hours(self):
        """Test formatting duration in hours."""
        assert TaskManager._format_duration(1 * 3600) == "1h 0m"
        assert TaskManager._format_duration(2 * 3600 + 30 * 60) == "2h 30m"
        assert TaskManager._format_duration(23 * 3600 + 59 * 60) == "23h 59m"

    def test_format_duration_days(self):
        """Test formatting duration in days."""
        assert TaskManager._format_duration(2 * 86400 + 3 * 3600) == "2d 3h"
        assert TaskManager._format_duration(10 * 86400) == "10d 0h"
        assert TaskManager._format_duration(1 * 86400 + 12 * 3600) == "1d 12h"
