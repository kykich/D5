"""Edge case tests for taskmanager."""

import os
import tempfile
import pytest

from taskmanager.models import Task, TaskManager
from taskmanager import storage


class TestEmptyStorage:
    """Tests for empty storage scenarios."""

    def test_list_empty_tasks(self):
        """Test listing tasks when none exist."""
        tm = TaskManager()
        tasks = tm.list_tasks()
        assert tasks == []

    def test_filter_empty_tasks(self):
        """Test filtering tasks when none exist."""
        tm = TaskManager()
        results = tm.filter_by_status("todo")
        assert results == []

    def test_search_empty_tasks(self):
        """Test searching tasks when none exist."""
        tm = TaskManager()
        results = tm.search("query")
        assert results == []

    def test_stats_empty_tasks(self):
        """Test stats when no tasks exist."""
        tm = TaskManager()
        stats = tm.stats()
        assert stats["total"] == 0
        assert stats["avg_days_open"] == 0.0

    def test_sort_empty_tasks(self):
        """Test sorting tasks when none exist."""
        tm = TaskManager()
        sorted_tasks = tm.sort_by_date("due_date")
        assert sorted_tasks == []


class TestInvalidInput:
    """Tests for invalid input handling."""

    def test_get_task_negative_index(self):
        """Test getting a task with negative index."""
        tm = TaskManager()
        tm.add_task("Task 1")
        assert tm.get_task(-1) is None

    def test_complete_nonexistent_task(self):
        """Test completing a nonexistent task."""
        tm = TaskManager()
        assert tm.complete_task(999) is False

    def test_delete_nonexistent_task(self):
        """Test deleting a nonexistent task."""
        tm = TaskManager()
        assert tm.delete_task(999) is False

    def test_from_dict_requires_created_at(self):
        """Test from_dict raises error when required fields are missing."""
        data = {"title": "Minimal Task"}
        with pytest.raises(KeyError):
            Task.from_dict(data)


class TestDuplicateScenarios:
    """Tests for duplicate-related scenarios."""

    def test_multiple_tasks_same_title(self):
        """Test having multiple tasks with the same title."""
        tm = TaskManager()
        tm.add_task("Same Title")
        tm.add_task("Same Title")
        assert len(tm.tasks) == 2

    def test_search_returns_all_matches(self):
        """Test search returns all matching tasks."""
        tm = TaskManager()
        tm.add_task("Buy milk")
        tm.add_task("Buy eggs")
        tm.add_task("Buy bread")
        results = tm.search("buy")
        assert len(results) == 3


class TestBoundaryConditions:
    """Tests for boundary conditions."""

    def test_single_task(self):
        """Test operations with a single task."""
        tm = TaskManager()
        tm.add_task("Only Task")
        assert len(tm.tasks) == 1
        tm.complete_task(0)
        assert tm.tasks[0].done is True

    def test_many_tasks(self):
        """Test with many tasks."""
        tm = TaskManager()
        for i in range(100):
            tm.add_task(f"Task {i}")
        assert len(tm.tasks) == 100
        results = tm.filter_by_status("todo")
        assert len(results) == 100

    def test_task_with_special_characters(self):
        """Test task with special characters in title."""
        tm = TaskManager()
        tm.add_task("Task with $pecial & chars!")
        assert tm.tasks[0].title == "Task with $pecial & chars!"

    def test_task_with_very_long_description(self):
        """Test task with very long description."""
        long_desc = "x" * 10000
        tm = TaskManager()
        tm.add_task("Long", description=long_desc)
        assert len(tm.tasks[0].description) == 10000

    def test_task_with_empty_title(self):
        """Test task with empty title (edge case)."""
        tm = TaskManager()
        task = tm.add_task("")
        assert task.title == ""

    def test_sort_by_created_at(self):
        """Test sorting by created_at."""
        tm = TaskManager()
        tm.add_task("Task 1")
        tm.add_task("Task 2")
        sorted_tasks = tm.sort_by_date("created_at")
        assert len(sorted_tasks) == 2

    def test_export_empty_tasks(self):
        """Test exporting when no tasks exist."""
        tm = TaskManager()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filepath = f.name
        try:
            tm.export_csv(filepath)
            with open(filepath, "r") as f:
                content = f.read()
            # Should have header even with no tasks
            assert "index,title" in content
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
