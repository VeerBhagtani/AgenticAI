# System Status Module

Query your system state in natural language. No dependencies beyond stdlib.

## Run
```bash
python main.py "is chrome open?"
python main.py "system status"
python main.py "is C:/Users/test.txt present?"
python main.py                   # interactive
```

## Supported Queries

| Query | Intent |
|---|---|
| `is chrome open?` | Check if process is running |
| `is notepad running?` | Check if process is running |
| `is report.txt present?` | Check file/folder existence |
| `system status` | CPU, RAM, disk snapshot |
| `list all processes` | Running processes (deduplicated) |
| `what windows are open?` | Visible window titles (Windows only) |
| `internet status` | Connectivity + local IP |

## Use From Other Modules
```python
from core.engine import StatusEngine

engine = StatusEngine()
result = engine.query("is chrome open?")

print(result["answer"])   # human-readable
print(result["success"])  # True/False
print(result["data"])     # raw data dict
```

## Response Fields
| Field | Description |
|---|---|
| `intent` | Detected query type |
| `answer` | Human-readable answer |
| `success` | True if app running / file exists / connected |
| `data` | Raw detection data for programmatic use |

## Platform Notes
- **Windows**: Full support — processes, windows, CPU/RAM via wmic
- **Linux/macOS**: Processes, file, system state, network — no window titles
