"""
Action handlers.
Each handler returns {"success": bool, "message": str}
"""

import os
import subprocess
import shutil


def ok(msg):  return {"success": True,  "message": msg}
def fail(msg): return {"success": False, "message": msg}


# ── App Launcher ──────────────────────────────────────────────
APP_ALIASES = {
    "notepad":   "notepad.exe",
    "calculator":"calc.exe",
    "calc":      "calc.exe",
    "paint":     "mspaint.exe",
    "explorer":  "explorer.exe",
    "browser":   "start chrome",
    "chrome":    "start chrome",
    "firefox":   "start firefox",
    "edge":      "start msedge",
    "word":      "start winword",
    "excel":     "start excel",
    "cmd":       "start cmd",
    "terminal":  "start wt",   # Windows Terminal
    "task manager": "taskmgr.exe",
}

def open_app(target: str) -> dict:
    app = APP_ALIASES.get(target.lower(), target)

    try:
        # Case 1: already using "start ..."
        if app.startswith("start "):
            subprocess.Popen(app, shell=True)

        else:
            try:
                # Try direct open
                subprocess.Popen([app], shell=True)
            except Exception:
                # Fallback to Windows start
                subprocess.Popen(f"start {app}", shell=True)

        return ok(f"Opened '{target}'")

    except Exception as e:
        return fail(f"Cannot open '{target}': {e}")


# ── CMD Runner ────────────────────────────────────────────────
def run_cmd(command: str) -> dict:
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = (result.stdout or result.stderr or "").strip()
        if result.returncode == 0:
            return ok(f"Command executed. Output:\n{output}" if output else "Command executed.")
        return fail(f"Exit code {result.returncode}. {output}")
    except subprocess.TimeoutExpired:
        return fail("Command timed out (30s limit).")
    except Exception as e:
        return fail(f"CMD error: {e}")


# ── File Operations ───────────────────────────────────────────
def create_file(path: str, content: str = "") -> dict:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return ok(f"Created: {path}")
    except Exception as e:
        return fail(f"Cannot create '{path}': {e}")


def delete_file(path: str) -> dict:
    try:
        if os.path.isfile(path):
            os.remove(path)
            return ok(f"Deleted file: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return ok(f"Deleted directory: {path}")
        return fail(f"Path not found: {path}")
    except Exception as e:
        return fail(f"Cannot delete '{path}': {e}")


def list_dir(path: str) -> dict:
    try:
        entries = os.listdir(path)
        listing = "\n".join(entries) if entries else "(empty)"
        return ok(f"Contents of '{path}':\n{listing}")
    except Exception as e:
        return fail(f"Cannot list '{path}': {e}")
