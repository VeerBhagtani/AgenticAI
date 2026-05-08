"""
Checker bridge — inline port of the checker rules so loop_controller
is self-contained (no external dependency on the checker project).
Returns {"success": bool, "quality": float, "message": str}
"""
import os, re, subprocess, platform
from collections import Counter

# ── File ─────────────────────────────────────────────────────
def check_file(params: dict) -> dict:
    path = params.get("path", "")
    if not path or not os.path.exists(path):
        return _r(False, 0.0, f"Not found: {path}")
    size = os.path.getsize(path) if os.path.isfile(path) else -1
    if size == 0:   quality = 0.1
    elif size < 10: quality = 0.4
    elif size < 1024: quality = 0.7
    else: quality = 1.0
    return _r(True, quality, f"Exists ({size} bytes): {path}")

# ── App / Process ─────────────────────────────────────────────
def check_app(params: dict) -> dict:
    proc = params.get("process", "").lower()
    if not proc:
        return _r(False, 0.0, "No process name")
    try:
        cmd = "tasklist" if platform.system() == "Windows" else "ps aux"
        out = subprocess.check_output(cmd, shell=True, text=True, timeout=10).lower()
        lines = [l for l in out.splitlines() if proc in l]
        if not lines:
            return _r(False, 0.0, f"Process not running: {proc}")
        q = min(1.0, 0.6 + len(lines) * 0.1)
        return _r(True, q, f"{proc} running ({len(lines)} instances)")
    except Exception as e:
        return _r(False, 0.0, str(e))

# ── Output / text match ───────────────────────────────────────
def check_output(params: dict) -> dict:
    expected = params.get("expected", "")
    source   = params.get("source", "")
    if os.path.isfile(source):
        try:
            source = open(source, encoding="utf-8", errors="ignore").read()
        except Exception as e:
            return _r(False, 0.0, str(e))
    if not source:
        return _r(False, 0.0, "Empty source")
    exact = expected.lower() in source.lower()
    words = expected.lower().split()
    matched = [w for w in words if w in source.lower()]
    ratio = len(matched) / max(len(words), 1)
    if exact:       q, ok = 1.0,  True
    elif ratio>=.8: q, ok = 0.75, True
    elif ratio>=.5: q, ok = 0.5,  True
    else:           q, ok = ratio*0.4, False
    return _r(ok, q, f"Match {len(matched)}/{len(words)} words")

# ── CMD output ────────────────────────────────────────────────
def check_cmd(params: dict) -> dict:
    command  = params.get("command", "")
    expected = params.get("expected", "")
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=20)
        out = (r.stdout + r.stderr).strip()
    except Exception as e:
        return _r(False, 0.0, str(e))
    base = 0.5 if r.returncode == 0 else 0.2
    if not expected:
        return _r(r.returncode == 0, min(1.0, base + 0.3), f"Exit {r.returncode}")
    exact = expected.lower() in out.lower()
    if exact:
        return _r(True, min(1.0, base + 0.5), "Exact match found")
    words   = expected.lower().split()
    matched = [w for w in words if w in out.lower()]
    ratio   = len(matched) / max(len(words), 1)
    q = min(1.0, base + ratio * 0.4)
    return _r(q >= 0.5, q, f"Partial match {len(matched)}/{len(words)}")

# ── Noop always passes ────────────────────────────────────────
def check_noop(params: dict) -> dict:
    return _r(True, 1.0, "Noop — always passes")

# ── Router ────────────────────────────────────────────────────
CHECKS = {
    "file":   check_file,
    "app":    check_app,
    "output": check_output,
    "cmd":    check_cmd,
    "noop":   check_noop,
}

def run_check(check_type: str, params: dict) -> dict:
    fn = CHECKS.get(check_type.lower())
    if not fn:
        return _r(False, 0.0, f"Unknown check type: {check_type}")
    return fn(params)

def _r(success, quality, message):
    return {"success": success, "quality": round(quality, 3), "message": message}
