# CLI Task Manager

A simple command-line task management tool built with Python.

## Installation

```bash
pip install -e .
```

Or install dependencies manually:

```bash
pip install -r requirements.txt
```

## Usage

### Add a task

```bash
python -m taskmanager.cli add "Buy groceries" -d "Milk, eggs, bread"
python -m taskmanager.cli add "Write tests" -p high
python -m taskmanager.cli add "Fix bug" -d "Critical issue" -D 2025-12-31T23:59:59 -p high
```

### List tasks

```bash
python -m taskmanager.cli list
python -m taskmanager.cli list -s todo
python -m taskmanager.cli list -s done
```

### Complete a task

```bash
python -m taskmanager.cli complete 0
```

### Delete a task

```bash
python -m taskmanager.cli delete 0
```

### Filter tasks

```bash
python -m taskmanager.cli filter todo
python -m taskmanager.cli filter-priority high
python -m taskmanager.cli sort-priority
```

### Sort tasks

```bash
python -m taskmanager.cli sort
python -m taskmanager.cli sort -k created_at
```

### Search tasks

```bash
python -m taskmanager.cli search "groceries"
```

### Show statistics

```bash
python -m taskmanager.cli stats
```

### Export to CSV

```bash
python -m taskmanager.cli export tasks.csv
```

## CLI Commands Reference

| Command | Description |
|---------|-------------|
| `add <title>` | Add a new task |
| `list` | List all tasks |
| `complete <index>` | Mark a task as complete |
| `delete <index>` | Delete a task |
| `filter <status>` | Filter by status (todo, in_progress, done) |
| `filter-priority <priority>` | Filter by priority (low, medium, high) |
| `sort [-k key]` | Sort by date (due_date, created_at) |
| `sort-priority` | Sort by priority (high -> low) |
| `stats` | Show task statistics |
| `search <query>` | Search tasks by keyword |
| `export <filename>` | Export to CSV |

## API Reference

### Task

```python
from taskmanager.models import Task

task = Task(
    title="My Task",
    description="Task description",
    status="todo",      # todo, in_progress, done
    priority="medium",  # low, medium, high
    due_date=datetime(2025, 12, 31),
)
task.mark_done()  # Mark as complete
```

### TaskManager

```python
from taskmanager.models import TaskManager

tm = TaskManager()
tm.add_task("Task 1", description="Desc", due_date="2025-12-31")
tm.complete_task(0)
tasks = tm.list_tasks()
filtered = tm.filter_by_status("done")
results = tm.search("keyword")
sorted_tasks = tm.sort_by_priority()
stats = tm.stats()
tm.export_csv("output.csv")
```

## Project Structure

```
taskmanager/
├── __init__.py      # Package init
├── models.py        # Task and TaskManager classes
├── storage.py       # JSON file storage
├── cli.py           # Command-line interface
├── utils.py         # Validation utilities
tests/
├── __init__.py
├── test_models.py   # Model unit tests
├── test_storage.py  # Storage unit tests
├── test_cli.py      # CLI integration tests
└── test_edge_cases.py  # Edge case tests
```

## Running Tests

```bash
python -m pytest
```

## License

MIT
