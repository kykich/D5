"""Unit tests for taskmanager.storage."""

import json
import os
import tempfile
import pytest

from taskmanager.models import Task
from taskmanager import storage


class TestSaveTasks:
    """Tests for save_tasks function."""

    def test_save_tasks_creates_file(self):
        """Test that save_tasks creates a file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name
        try:
            tasks = [Task(title="Task 1"), Task(title="Task 2")]
            storage.save_tasks(tasks, filepath)
            assert os.path.exists(filepath)
            with open(filepath, "r") as f:
                data = json.load(f)
            assert len(data) == 2
        finally:
            os.remove(filepath)

    def test_save_tasks_empty_list(self):
        """Test saving an empty list of tasks."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name
        try:
            storage.save_tasks([], filepath)
            with open(filepath, "r") as f:
                data = json.load(f)
            assert data == []
        finally:
            os.remove(filepath)


class TestLoadTasks:
    """Tests for load_tasks function."""

    def test_load_tasks_nonexistent_file(self):
        """Test loading from a nonexistent file returns empty list."""
        tasks = storage.load_tasks("/nonexistent/path/tasks.json")
        assert tasks == []

    def test_load_tasks_valid_file(self):
        """Test loading from a valid file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump([
                {"title": "Task 1", "description": "", "status": "todo",
                 "priority": "medium", "created_at": "2025-01-01T00:00:00",
                 "due_date": None, "completed_at": None, "done": False}
            ], f)
            filepath = f.name
        try:
            tasks = storage.load_tasks(filepath)
            assert len(tasks) == 1
            assert tasks[0].title == "Task 1"
        finally:
            os.remove(filepath)

    def test_load_tasks_multiple_tasks(self):
        """Test loading multiple tasks."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump([
                {"title": f"Task {i}", "description": "", "status": "todo",
                 "priority": "medium", "created_at": "2025-01-01T00:00:00",
                 "due_date": None, "completed_at": None, "done": False}
                for i in range(5)
            ], f)
            filepath = f.name
        try:
            tasks = storage.load_tasks(filepath)
            assert len(tasks) == 5
        finally:
            os.remove(filepath)


class TestAppendTask:
    """Tests for append_task function."""

    def test_append_task_new_file(self):
        """Test appending to a nonexistent file creates it."""
        filepath = tempfile.mktemp(suffix=".json")
        try:
            storage.append_task({"title": "New Task"}, filepath)
            with open(filepath, "r") as f:
                data = json.load(f)
            assert len(data) == 1
            assert data[0]["title"] == "New Task"
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    def test_append_task_existing_file(self):
        """Test appending to an existing file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            json.dump([{"title": "Existing"}], f)
            filepath = f.name
        try:
            storage.append_task({"title": "New Task"}, filepath)
            with open(filepath, "r") as f:
                data = json.load(f)
            assert len(data) == 2
            assert data[1]["title"] == "New Task"
        finally:
            os.remove(filepath)
