"""
Rule: CMD
Runs a command and checks if output contains expected text.
"""
import subprocess

def check(params: dict) -> dict:
    command  = params.get("command", "").strip()
    expected = params.get("expected", "").strip()

    if not command:
        return _fail("No command provided.", 0.0)

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True,
            text=True, timeout=20
        )
        output = (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return _fail("Command timed out.", 0.0)
    except Exception as e:
        return _fail(f"Command error: {e}", 0.0)

    # ── Base quality from exit code ───────────────────────────
    base = 0.5 if result.returncode == 0 else 0.2

    if not expected:
        quality = base + (0.3 if output else 0.0)
        return {
            "success":   result.returncode == 0,
            "rule_name": "cmd_output",
            "quality":   round(min(1.0, quality), 3),
            "message":   f"Exit code {result.returncode}. Output length: {len(output)} chars",
            "details":   output[:300]
        }

    # ── Check expected in output ──────────────────────────────
    words         = expected.lower().split()
    matched       = [w for w in words if w in output.lower()]
    ratio         = len(matched) / max(len(words), 1)
    exact         = expected.lower() in output.lower()

    if exact:
        quality = min(1.0, base + 0.5)
        match   = "exact"
    elif ratio >= 0.8:
        quality = min(1.0, base + 0.35)
        match   = f"partial ({len(matched)}/{len(words)})"
    else:
        quality = base * ratio
        match   = f"weak ({len(matched)}/{len(words)})"

    return {
        "success":   quality >= 0.5,
        "rule_name": "cmd_output",
        "quality":   round(quality, 3),
        "message":   f"Match: {match} | Exit: {result.returncode}",
        "details":   output[:300]
    }

def _fail(msg, quality):
    return {"success": False, "rule_name": "cmd_output",
            "quality": quality, "message": msg, "details": ""}
