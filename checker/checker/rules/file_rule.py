"""
Rule: FILE
Checks if a file exists and evaluates its quality (size, readability, content).
"""
import os

def check(params: dict) -> dict:
    path = params.get("path", "")

    if not path:
        return _fail("No path provided.", 0.0)

    if not os.path.exists(path):
        return _fail(f"Path does not exist: {path}", 0.0)

    # ── Quality checks ────────────────────────────────────────
    quality = 0.0
    details = []

    if os.path.isfile(path):
        size = os.path.getsize(path)
        details.append(f"size={size} bytes")

        if size == 0:
            quality = 0.1
            details.append("file is empty")
        elif size < 10:
            quality = 0.4
            details.append("file is very small")
        elif size < 1024:
            quality = 0.7
        else:
            quality = 1.0

        # Try reading (checks if file is valid/not corrupt)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(512)
            if content.strip():
                quality = min(1.0, quality + 0.05)
                details.append("readable content confirmed")
        except Exception:
            quality = max(0.0, quality - 0.2)
            details.append("could not read file")

    elif os.path.isdir(path):
        entries = os.listdir(path)
        quality = min(1.0, 0.3 + len(entries) * 0.1)
        details.append(f"directory with {len(entries)} entries")

    return {
        "success":    True,
        "rule_name":  "file_exists",
        "quality":    round(quality, 3),
        "message":    f"Path exists: {path}",
        "details":    ", ".join(details)
    }

def _fail(msg, quality):
    return {"success": False, "rule_name": "file_exists",
            "quality": quality, "message": msg, "details": ""}
