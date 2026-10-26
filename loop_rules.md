# Execution Loop Rules — Default (Run 1)

## General Rules
1. Always read the full file before editing
2. Run tests after every change
3. If a test fails, fix it before committing
4. Check git status before and after each task
5. Commit only changes related to the current task

## Bug Fixes
- Understand the bug before fixing
- Reproduce the bug first if possible
- Fix the root cause, not the symptom
- Verify fix doesn't break other functionality

## Features
- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation
- Keep changes minimal and focused

## Tests
- Use pytest
- Follow Arrange-Act-Assert pattern
- Cover edge cases
- Use tempfile for file-based tests

## Commit Messages
- Format: `task(TASK-ID): <description>`
- Keep messages concise

## Code Quality
- Don't introduce new bugs
- Keep existing API unchanged
- Use existing imports and patterns
- Don't add unnecessary dependencies
