"""Integration tests for CLI commands."""

import subprocess
import sys
import os
import tempfile
import pytest

CLI_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "taskmanager", "cli.py")


def run_cli(*args):
    """Run the CLI with given arguments and return the result."""
    cmd = [sys.executable, "-m", "taskmanager.cli"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), ".."))
    return result


class TestCLIAdd:
    """Tests for the 'add' CLI command."""

    def test_add_task(self):
        """Test adding a task via CLI."""
        result = run_cli("add", "Test Task", "-d", "Description")
        assert result.returncode == 0
        assert "Task added" in result.stdout

    def test_add_task_with_priority(self):
        """Test adding a task with priority."""
        result = run_cli("add", "Test Task", "-p", "high")
        assert result.returncode == 0
        assert "priority: high" in result.stdout


class CLIList:
    """Tests for the 'list' CLI command."""

    def setup_method(self):
        """Set up test fixtures by adding tasks."""
        run_cli("add", "Task 1")
        run_cli("add", "Task 2")

    def test_list_tasks(self):
        """Test listing all tasks."""
        result = run_cli("list")
        assert result.returncode == 0
        assert "Task 1" in result.stdout
        assert "Task 2" in result.stdout

    def test_list_empty(self):
        """Test listing when no tasks exist."""
        # Remove tasks file
        if os.path.exists("tasks_data.json"):
            os.remove("tasks_data.json")
        result = run_cli("list")
        assert "No tasks found" in result.stdout


class TestCLIComplete:
    """Tests for the 'complete' CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        run_cli("add", "Task to complete")

    def test_complete_task(self):
        """Test completing a task."""
        result = run_cli("complete", "0")
        assert result.returncode == 0
        assert "Task completed" in result.stdout


class TestCLIDelete:
    """Tests for the 'delete' CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        run_cli("add", "Task to delete")

    def test_delete_task(self):
        """Test deleting a task."""
        result = run_cli("delete", "0")
        assert result.returncode == 0
        assert "Task deleted" in result.stdout


class TestCLIStats:
    """Tests for the 'stats' CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clean up any existing tasks
        if os.path.exists("tasks_data.json"):
            os.remove("tasks_data.json")
        run_cli("add", "Task 1")
        run_cli("add", "Task 2")

    def test_stats_command(self):
        """Test stats command output."""
        result = run_cli("stats")
        assert result.returncode == 0
        assert "Task Statistics" in result.stdout
        assert "Total: 2" in result.stdout


class TestCLISearch:
    """Tests for the 'search' CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        run_cli("add", "Buy groceries")
        run_cli("add", "Walk the dog")

    def test_search_found(self):
        """Test search when task is found."""
        result = run_cli("search", "groceries")
        assert result.returncode == 0
        assert "Buy groceries" in result.stdout

    def test_search_not_found(self):
        """Test search when task is not found."""
        result = run_cli("search", "nonexistent")
        assert result.returncode == 0
        assert "No tasks found" in result.stdout


class TestCLIExport:
    """Tests for the 'export' CLI command."""

    def setup_method(self):
        """Set up test fixtures."""
        run_cli("add", "Task to export")

    def test_export_csv(self):
        """Test exporting to CSV."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            filepath = f.name
        try:
            result = run_cli("export", filepath)
            assert result.returncode == 0
            assert "Exported" in result.stdout
            assert os.path.exists(filepath)
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
