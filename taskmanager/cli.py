"""Command-line interface for Task Manager."""

import argparse
import sys
from datetime import datetime

from .models import TaskManager
from . import storage
from .utils import validate_task_index, validate_status, check_task_exists


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(description="CLI Task Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add task
    add_p = subparsers.add_parser("add", help="Add a new task")
    add_p.add_argument("title", help="Task title")
    add_p.add_argument("-d", "--description", default="", help="Task description")
    add_p.add_argument("-D", "--due", help="Due date (ISO format: YYYY-MM-DDTHH:MM)")
    add_p.add_argument("-p", "--priority", default="medium", help="Priority (low, medium, high)")

    # List tasks
    list_p = subparsers.add_parser("list", help="List all tasks")
    list_p.add_argument("-s", "--status", help="Filter by status")

    # Complete task
    complete_p = subparsers.add_parser("complete", help="Mark a task as complete")
    complete_p.add_argument("index", type=int, help="Task index")

    # Delete task
    delete_p = subparsers.add_parser("delete", help="Delete a task")
    delete_p.add_argument("index", type=int, help="Task index")

    # Filter by status
    filter_p = subparsers.add_parser("filter", help="Filter tasks by status")
    filter_p.add_argument("status", help="Status to filter by")

    # Sort by date
    sort_p = subparsers.add_parser("sort", help="Sort tasks by date")
    sort_p.add_argument("-k", "--key", default="due_date", help="Sort key (due_date, created_at)")

    # Filter by priority
    filter_pri_p = subparsers.add_parser("filter-priority", help="Filter tasks by priority")
    filter_pri_p.add_argument("priority", help="Priority to filter by (low, medium, high)")

    # Sort by priority
    sort_pri_p = subparsers.add_parser("sort-priority", help="Sort tasks by priority")

    # Stats
    subparsers.add_parser("stats", help="Show task statistics")

    # Search
    search_p = subparsers.add_parser("search", help="Search tasks by keyword")
    search_p.add_argument("query", help="Search query")

    # Export
    export_p = subparsers.add_parser("export", help="Export tasks to CSV")
    export_p.add_argument("filename", help="Output CSV filename")

    return parser


def handle_add(args, manager):
    """Handle the 'add' command."""
    task = manager.add_task(args.title, args.description, args.due)
    task.priority = args.priority
    storage.save_tasks(manager.tasks)
    print(f"Task added: {task.title} (index {len(manager.tasks) - 1}) [priority: {task.priority}]")


def handle_list(args, manager):
    """Handle the 'list' command."""
    if args.status:
        validate_status(args.status)
        tasks = manager.filter_by_status(args.status)
    else:
        tasks = manager.list_tasks()

    if not tasks:
        print("No tasks found.")
    else:
        for i, task in enumerate(tasks):
            status_icon = "x" if task.done else " "
            due = task.due_date.strftime("%Y-%m-%d") if task.due_date else "no due date"
            print(f"[{status_icon}] {i}: {task.title} - {task.status} (due: {due})")
            if task.description:
                print(f"    {task.description}")


def handle_complete(args, manager):
    """Handle the 'complete' command."""
    idx = validate_task_index(str(args.index))
    if check_task_exists(manager, idx):
        if manager.complete_task(idx):
            storage.save_tasks(manager.tasks)
            print(f"Task completed: {manager.tasks[idx].title}")
        else:
            print("Failed to complete task.")


def handle_delete(args, manager):
    """Handle the 'delete' command."""
    idx = validate_task_index(str(args.index))
    if check_task_exists(manager, idx):
        if manager.delete_task(idx):
            storage.save_tasks(manager.tasks)
            print("Task deleted.")
        else:
            print("Failed to delete task.")


def handle_filter(args, manager):
    """Handle the 'filter' command."""
    validate_status(args.status)
    tasks = manager.filter_by_status(args.status)
    if not tasks:
        print(f"No tasks with status '{args.status}'.")
    else:
        print(f"Tasks with status '{args.status}':")
        for i, task in enumerate(tasks):
            print(f"  {i}: {task.title}")


def handle_sort(args, manager):
    """Handle the 'sort' command."""
    try:
        sorted_tasks = manager.sort_by_date(args.key)
        print(f"Tasks sorted by {args.key}:")
        for i, task in enumerate(sorted_tasks):
            print(f"  {i}: {task.title}")
    except AttributeError as e:
        print(f"Error sorting: {e}")


def handle_filter_priority(args, manager):
    """Handle the 'filter-priority' command."""
    tasks = manager.filter_by_priority(args.priority)
    if not tasks:
        print(f"No tasks with priority '{args.priority}'.")
    else:
        print(f"Tasks with priority '{args.priority}':")
        for i, task in enumerate(tasks):
            print(f"  {i}: {task.title} [{task.priority}]")


def handle_sort_priority(args, manager):
    """Handle the 'sort-priority' command."""
    sorted_tasks = manager.sort_by_priority()
    print("Tasks sorted by priority (high -> low):")
    for i, task in enumerate(sorted_tasks):
        print(f"  {i}: {task.title} [{task.priority}]")


def handle_stats(args, manager):
    """Handle the 'stats' command."""
    stats = manager.stats()
    print("Task Statistics:")
    print(f"  Total: {stats['total']}")
    print(f"  To Do: {stats['by_status']['todo']}")
    print(f"  In Progress: {stats['by_status']['in_progress']}")
    print(f"  Done: {stats['by_status']['done']}")
    print(f"  Avg Days Open: {stats['avg_days_open']}")
    print(f"  Overdue: {stats['overdue_count']}")


def handle_search(args, manager):
    """Handle the 'search' command."""
    results = manager.search(args.query)
    if not results:
        print(f"No tasks found matching '{args.query}'.")
    else:
        print(f"Tasks matching '{args.query}':")
        for i, task in enumerate(results):
            print(f"  {i}: {task.title} - {task.description}")


def handle_export(args, manager):
    """Handle the 'export' command."""
    try:
        with open(args.filename, "w", encoding="utf-8") as f:
            f.write("index,title,description,status,created_at,due_date,completed_at,done\n")
            for i, task in enumerate(manager.tasks):
                due = task.due_date.strftime("%Y-%m-%d") if task.due_date else ""
                completed = task.completed_at.strftime("%Y-%m-%d") if task.completed_at else ""
                f.write(f"{i},{task.title},{task.description},{task.status},{task.created_at.isoformat()},{due},{completed},{task.done}\n")
        print(f"Exported {len(manager.tasks)} tasks to {args.filename}")
    except IOError as e:
        print(f"Error exporting: {e}")


def main():
    """Main entry point for the CLI."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Load tasks from storage
    manager = TaskManager()
    loaded_tasks = storage.load_tasks()
    manager.tasks = loaded_tasks

    # Command dispatch table
    handlers = {
        "add": handle_add,
        "list": handle_list,
        "complete": handle_complete,
        "delete": handle_delete,
        "filter": handle_filter,
        "sort": handle_sort,
        "filter-priority": handle_filter_priority,
        "sort-priority": handle_sort_priority,
        "stats": handle_stats,
        "search": handle_search,
        "export": handle_export,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args, manager)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
