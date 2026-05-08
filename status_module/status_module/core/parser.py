"""
Query parser — maps natural language questions to structured queries.

Supported intents:
  is_running   → "is chrome open?" / "is notepad running?"
  is_file      → "is report.txt present?" / "does C:/file.txt exist?"
  system_state → "what is cpu usage?" / "system status"
  process_list → "list all processes" / "what apps are running?"
  network      → "am I connected?" / "internet status"
  windows_list → "what windows are open?" / "open windows"
"""
import re

def parse(query: str) -> dict:
    q = query.strip().lower()

    # ── is_running ────────────────────────────────────────────
    m = re.search(
        r"\b(is|check if|check)\b.+?\b(open|running|active|launched|started|on)\b",
        q
    )
    if m:
        # Extract app name between "is" and "open/running"
        app = re.sub(
            r"\b(is|check if|check|open|running|active|launched|started|on|app|application|process)\b",
            "", q
        ).strip(" ?")
        return {"intent": "is_running", "target": app or query}

    # ── is_file ───────────────────────────────────────────────
    m = re.search(
        r"\b(is|does|check)\b.+\b(file|folder|directory|present|exist|there)\b",
        q
    )
    if m:
        # Try to extract a path (anything with / \ . or looks like a filename)
        path_m = re.search(r"([a-z]:[\\\/][^\s?]+|[^\s?]+\.[a-z]{1,5}|\/[^\s?]+)", q)
        path = path_m.group(1) if path_m else query.strip(" ?")
        return {"intent": "is_file", "target": path}

    # ── process_list ──────────────────────────────────────────
    if re.search(r"(list|show|what).*(process|app|running)", q) or \
       re.search(r"(process|app).*(list|running|all)", q):
        return {"intent": "process_list"}

    # ── windows_list ──────────────────────────────────────────
    if re.search(r"\b(open|visible|current|all).+\bwindow", q) or \
       re.search(r"\bwindow.+(open|list|show|running)\b", q):
        return {"intent": "windows_list"}

    # ── network ───────────────────────────────────────────────
    if re.search(r"\b(internet|connected|connection|network|online|offline|wifi)\b", q):
        return {"intent": "network"}

    # ── system_state ─────────────────────────────────────────
    if re.search(r"\b(cpu|ram|memory|disk|system|status|usage|uptime|platform)\b", q):
        return {"intent": "system_state"}

    # ── Fallback: treat as is_running if it contains an app-like word ─
    if re.search(r"\b(chrome|firefox|edge|notepad|excel|word|calc|paint|vlc|"
                 r"slack|zoom|vscode|python|node|java)\b", q):
        return {"intent": "is_running", "target": q.strip(" ?")}

    return {"intent": "unknown", "raw": query}
