# PC Control Agent

Zero-dependency Python agent for Windows system control.

## Setup
```
pip install -r requirements.txt   # nothing external needed
python agent.py                   # interactive mode
python agent.py "open notepad"    # single command
```

## Supported Commands

| Natural Language                              | Action         |
|-----------------------------------------------|----------------|
| `open notepad`                                | Launch app     |
| `open chrome`                                 | Launch browser |
| `run ipconfig`                                | CMD command    |
| `run mkdir C:\test`                           | CMD command    |
| `create file C:\test\hello.txt`               | Create file    |
| `create file notes.txt with content Hello!`   | Create w/ text |
| `delete file C:\test\hello.txt`               | Delete file    |
| `list files in C:\Users`                      | List directory |

## Risky Commands
Commands containing `del`, `delete`, `rmdir`, `shutdown`, `taskkill`, etc. 
require explicit `yes` confirmation before executing.

## Logs
Stored in `logs/agent_YYYYMMDD.log`

## Adding New Actions
1. Add handler function in `core/actions.py`
2. Add parser rule in `core/parser.py`
3. Register in `PCController._handlers` in `core/controller.py`
