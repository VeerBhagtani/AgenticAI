"""
Parser: maps natural language commands to structured actions.

Supported intents:
  open_app   → open <app>
  run_cmd    → run/execute <command>
  create_file → create file <path> [with content ...]
  delete_file → delete file <path>
  list_dir   → list files in <path>
  unknown    → fallback
"""

import re

def parse(command: str) -> dict:
    cmd = command.strip()
    lower = cmd.lower()

    # open <app>
    m = re.match(r"^open\s+(.+)$", lower)
    if m:
        return {"action": "open_app", "target": m.group(1).strip()}

    # run/execute <cmd>
    m = re.match(r"^(?:run|execute|cmd)\s+(.+)$", lower, re.IGNORECASE)
    if m:
        return {"action": "run_cmd", "command": cmd[m.start(1):]}

    # create file <path> [with content <text>]
    m = re.match(r"^create\s+file\s+(\S+)(?:\s+with\s+content\s+(.+))?$", lower)
    if m:
        path = cmd.split()[2]  # preserve original case
        content = m.group(2) or ""
        return {"action": "create_file", "path": path, "content": content}

    # delete file <path>
    m = re.match(r"^delete\s+file\s+(\S+)$", lower)
    if m:
        path = cmd.split()[2]
        return {"action": "delete_file", "path": path}

    # list files in <path>
    m = re.match(r"^list(?:\s+files?)?\s+(?:in\s+)?(.+)$", lower)
    if m:
        return {"action": "list_dir", "path": m.group(1).strip()}

    return {"action": "unknown", "raw": cmd}
