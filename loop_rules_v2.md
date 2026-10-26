# Execution Loop Rules — Improved (Run 2)

## General
1. Always read the full file before editing — understand context first
2. Run tests after EVERY change — `python -m pytest --tb=short`
3. If a test fails, fix it before committing
4. Check git status before and after each task
5. Commit only changes related to the current task
6. Use `python -c "import sys; sys.path.insert(0, '.'); import taskmanager"` to verify import works
7. When adding CLI args, update both the parser AND the handler

## Bug Fixes
- Understand the bug before fixing
- Reproduce the bug first if possible (write a failing test)
- Fix the root cause, not the symptom
- Verify fix doesn't break other functionality
- Run ALL tests after fix, not just related ones

## Features
- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation
- Keep changes minimal and focused
- When modifying dataclass fields, update BOTH to_dict() AND from_dict()
- When adding CLI commands, add BOTH subparser AND handler function

## Tests
- Use pytest
- Follow Arrange-Act-Assert pattern
- Cover edge cases
- Use tempfile for file-based tests
- Clean up test fixtures (remove tasks_data.json) in setup_method
- Use `python -m taskmanager.cli` not direct file execution for CLI tests
- When tests fail, read the error message and fix the test or the code

## Refactoring
- Extract functions to keep each handler <= 60 lines
- Don't duplicate validation logic — use shared utils
- Add type hints to ALL public functions
- Import from utils.py for shared functions

## Documentation
- Google-style docstrings for all public functions
- Include Args, Returns, Raises sections
- Update README with new features
- Document CLI commands in a table

## Common Pitfalls (from Run 1)
1. When modifying Task dataclass, always update to_dict() and from_dict() together
2. CLI tests must use `python -m taskmanager.cli`, not direct file execution
3. Clean up tasks_data.json between CLI test methods
4. pytest must be installed before running tests
5. When adding fields to dataclass, remember to handle them in serialization
