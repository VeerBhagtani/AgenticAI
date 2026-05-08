"""
Rule: APP
Checks if an application/process is currently running.
Works on Windows (tasklist) and Linux/macOS (ps).
"""
import subprocess
import platform

def check(params: dict) -> dict:
    process = params.get("process", "").lower().strip()
    if not process:
        return _fail("No process name provided.", 0.0)

    system = platform.system()

    try:
        if system == "Windows":
            out = subprocess.check_output("tasklist", shell=True, text=True, timeout=10)
        else:
            out = subprocess.check_output(["ps", "aux"], text=True, timeout=10)
    except Exception as e:
        return _fail(f"Could not query processes: {e}", 0.0)

    # Match process name (fuzzy — check if query is substring of any line)
    matching_lines = [line for line in out.lower().splitlines() if process in line]

    if not matching_lines:
        return _fail(f"Process not found: '{process}'", 0.0)

    # ── Quality: how many instances, is it responsive ─────────
    count = len(matching_lines)
    quality = min(1.0, 0.6 + count * 0.1)

    return {
        "success":   True,
        "rule_name": "app_running",
        "quality":   round(quality, 3),
        "message":   f"Process '{process}' is running ({count} instance(s))",
        "details":   matching_lines[0].strip()
    }

def _fail(msg, quality):
    return {"success": False, "rule_name": "app_running",
            "quality": quality, "message": msg, "details": ""}
