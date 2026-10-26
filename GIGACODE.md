# GIGACODE.md — day5

## Команды
```
pip install pytest          # pytest нет в requirements.txt — ставить вручную
python -m pytest            # запустить все тесты
python -m pytest --tb=short # тесты с коротким трейсом
python -m taskmanager.cli   # запуск CLI
```

## Архитектура
- `taskmanager/models.py` — `Task` (dataclass), `TaskManager`
- `taskmanager/storage.py` — JSON-хранилище (`tasks_data.json`)
- `taskmanager/cli.py` — argparse CLI, обработчики `handle_*`
- `taskmanager/utils.py` — валидация (`validate_task_index`, `validate_status`, `check_task_exists`)
- `tests/` — 4 файла, 56 тестов

## Важные правила
- При добавлении поля в `Task` — обновляй `to_dict()` И `from_dict()` вместе
- CLI-тесты используют `python -m taskmanager.cli`, не прямой запуск файла
- CLI-тесты чистят `tasks_data.json` в `setup_method`
- При добавлении CLI-команды — добавляй и subparser, и handler
- Commit-сообщения: `task(TASK-ID): <description>`

## Трекер задач
- `tasks.json` — локальный трекер (16 задач: 3 bug, 4 feature, 3 refactor, 4 test, 2 docs)
- GitVerse API **не** GitLab-совместимый — все endpoints возвращают HTML, не JSON
- Создать issues через web UI: `https://gitverse.ru/Mkelembembe/day5/issues`

## Окружение
- Windows, PowerShell
- Python 3.14.7
