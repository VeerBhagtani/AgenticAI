# Memory System

SQLite-backed task memory for AI agents. Records every task with full context and supports fuzzy retrieval of similar past tasks.

## Run
```bash
python main.py demo     # seed with sample data + show retrieval
python main.py          # interactive CLI
```

## CLI Commands
| Command | Description |
|---|---|
| `record` | Manually add a task |
| `recall` | Search for similar past tasks by keyword |
| `recent` | List N most recent tasks |
| `get <id>` | Full detail view of one task |
| `stats` | Aggregate success/quality stats |
| `delete <id>` | Remove a task |

## Use From Other Modules
```python
from memory_manager import MemoryManager
mm = MemoryManager()

# Start timer
mm.start_task("open notepad")

# Record when done
task_id = mm.record(
    goal          = "open notepad",
    command       = "open notepad",
    category      = "PC_AGENT",       # WEB_AGENT | PC_AGENT | BOTH
    success       = True,
    quality_score = 0.95,
    retries       = 0,
    output        = "notepad.exe launched",
    steps=[
        {"name": "Launch", "action": "notepad.exe",
         "success": True, "output": "OK", "error": ""}
    ]
)

# Find similar past tasks
similar = mm.recall("launch application")

# Stats
mm.stats()
```

## DB Schema
```
tasks       — goal, category, command, success, quality_score, retries, duration, output, error
task_steps  — step-level detail per task
tags        — auto-extracted keyword tags for retrieval
```

DB stored at `db/memory.db` (SQLite, zero setup).

## Retrieval Logic
1. Auto-extracts keywords (tags) from goal + command
2. On recall: matches by tag overlap → ranks by match count
3. Falls back to LIKE substring match if not enough results
