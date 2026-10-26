"""Pytest hook for automatic task status updates in tasks.json."""

import json
from pathlib import Path

_config = None

TASK_TEST_MAP = {
    "BUG-1": ["test_mark_done_sets_completed_at"],
    "BUG-2": ["test_filter_by_status_case_insensitive"],
    "BUG-3": ["test_sort_by_date_with_none"],
    "FEAT-1": ["test_search", "test_search_case_insensitive"],
    "FEAT-2": ["test_filter_by_priority", "test_sort_by_priority"],
    "FEAT-3": ["test_export_csv", "test_export_empty_tasks"],
    "FEAT-4": ["test_stats", "test_stats_empty_tasks", "test_stats_command"],
    "TEST-1": [
        "test_create_task_default_values", "test_create_task_with_values",
        "test_to_dict", "test_from_dict", "test_from_dict_with_due_date",
        "test_add_task", "test_add_task_with_due_date", "test_get_task_valid_index",
        "test_get_task_invalid_index", "test_complete_task", "test_complete_task_invalid_index",
        "test_delete_task", "test_delete_task_invalid_index", "test_list_tasks",
        "test_count_by_status",
    ],
    "TEST-2": [
        "test_save_tasks_creates_file", "test_save_tasks_empty_list",
        "test_load_tasks_nonexistent_file", "test_load_tasks_valid_file",
        "test_load_tasks_multiple_tasks", "test_append_task_new_file",
        "test_append_task_existing_file",
    ],
    "TEST-3": [
        "test_add_task", "test_add_task_with_priority", "test_list_tasks",
        "test_list_empty", "test_complete_task", "test_delete_task",
        "test_stats_command", "test_search_found", "test_search_not_found",
        "test_export_csv",
    ],
    "TEST-4": [
        "test_list_empty_tasks", "test_filter_empty_tasks", "test_search_empty_tasks",
        "test_stats_empty_tasks", "test_sort_empty_tasks", "test_get_task_negative_index",
        "test_complete_nonexistent_task", "test_delete_nonexistent_task",
        "test_from_dict_requires_created_at", "test_multiple_tasks_same_title",
        "test_search_returns_all_matches", "test_single_task", "test_many_tasks",
        "test_task_with_special_characters", "test_task_with_very_long_description",
        "test_task_with_empty_title", "test_sort_by_created_at", "test_export_empty_tasks",
    ],
}


def pytest_configure(config):
    """Store config reference for use in other hooks."""
    global _config
    _config = config


def pytest_runtest_logreport(report):
    """Track tests that passed."""
    if report.when == "call" and report.passed:
        test_name = report.nodeid.split("::")[-1]
        if _config is not None:
            if not hasattr(_config, "passed_tests"):
                _config.passed_tests = set()
            _config.passed_tests.add(test_name)


def pytest_sessionfinish(session, exitstatus):
    """Update task statuses in tasks.json when related tests pass."""
    passed_tests = getattr(session.config, "passed_tests", set())

    tasks_path = Path("tasks.json")
    if not tasks_path.exists():
        return

    with open(tasks_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated = False
    for task_id, test_names in TASK_TEST_MAP.items():
        if any(name in passed_tests for name in test_names):
            for task in data["tasks"]:
                if task["id"] == task_id and task["status"] != "done":
                    task["status"] = "done"
                    updated = True
                    break

    if updated:
        with open(tasks_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
