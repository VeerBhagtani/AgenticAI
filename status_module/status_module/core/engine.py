"""
StatusEngine — routes parsed query to correct detector and formats response.
"""
from core.parser    import parse
from core.detectors import (
    is_process_running, get_processes,
    get_open_windows, is_file_present,
    get_system_state, get_network_state
)
from core.logger import Logger


class StatusEngine:
    def __init__(self):
        self.logger = Logger()

    def query(self, question: str) -> dict:
        log = self.logger
        log.info(f"QUERY: {question}")

        parsed = parse(question)
        intent = parsed.get("intent")
        log.info(f"INTENT: {intent} | parsed={parsed}")

        handlers = {
            "is_running":   self._is_running,
            "is_file":      self._is_file,
            "process_list": self._process_list,
            "windows_list": self._windows_list,
            "system_state": self._system_state,
            "network":      self._network,
        }

        handler = handlers.get(intent)
        if not handler:
            return self._unknown(question)

        result = handler(parsed)
        log.info(f"RESULT: {result.get('answer','')}")
        return result

    # ── Handlers ──────────────────────────────────────────────

    def _is_running(self, p: dict) -> dict:
        target = p.get("target", "")
        data   = is_process_running(target)
        yes    = data["running"]
        answer = (
            f"✅ YES — '{target}' is running ({data['count']} instance(s))."
            if yes else
            f"❌ NO — '{target}' is not running."
        )
        return {
            "intent":  "is_running",
            "answer":  answer,
            "success": yes,
            "data":    data,
        }

    def _is_file(self, p: dict) -> dict:
        path = p.get("target", "")
        data = is_file_present(path)
        if data["exists"]:
            kind = "file" if data["is_file"] else "directory"
            size = f" ({data['size_bytes']} bytes)" if data["size_bytes"] is not None else ""
            answer = f"✅ YES — {kind} exists{size}. Last modified: {data['modified']}"
        else:
            answer = f"❌ NO — '{path}' does not exist."
        return {
            "intent":  "is_file",
            "answer":  answer,
            "success": data["exists"],
            "data":    data,
        }

    def _process_list(self, p: dict) -> dict:
        procs = get_processes()
        # Deduplicate by name
        seen  = {}
        for pr in procs:
            name = pr.get("name", "?")
            seen[name] = seen.get(name, 0) + 1
        top = sorted(seen.items(), key=lambda x: x[1], reverse=True)[:30]
        lines = [f"  {n} ({c} instance{'s' if c>1 else ''})" for n, c in top]
        answer = f"Running processes ({len(seen)} unique):\n" + "\n".join(lines)
        return {
            "intent":  "process_list",
            "answer":  answer,
            "success": True,
            "data":    {"unique_count": len(seen), "top": top},
        }

    def _windows_list(self, p: dict) -> dict:
        windows = get_open_windows()
        if not windows:
            answer = "No open windows detected."
        else:
            lines  = "\n".join(f"  • {w}" for w in windows[:20])
            answer = f"Open windows ({len(windows)}):\n{lines}"
        return {
            "intent":  "windows_list",
            "answer":  answer,
            "success": True,
            "data":    {"windows": windows},
        }

    def _system_state(self, p: dict) -> dict:
        s = get_system_state()
        answer = (
            f"System Status\n"
            f"  Platform   : {s['platform']} {s['os_version'][:40]}\n"
            f"  Hostname   : {s['hostname']}\n"
            f"  CPU        : {s['cpu_percent']}% | {s['cpu_count']} cores\n"
            f"  RAM        : {s['ram_used_pct']}% used "
            f"({s['ram_free_mb']} MB free / {s['ram_total_mb']} MB total)\n"
            f"  Disk       : {s['disk_used_pct']}% used "
            f"({s['disk_free_gb']} GB free / {s['disk_total_gb']} GB total)\n"
            f"  Timestamp  : {s['timestamp'][:19]}"
        )
        return {
            "intent":  "system_state",
            "answer":  answer,
            "success": True,
            "data":    s,
        }

    def _network(self, p: dict) -> dict:
        n = get_network_state()
        status = "✅ Connected" if n["internet"] else "❌ No internet"
        answer = f"Network: {status} | Local IP: {n['local_ip']}"
        return {
            "intent":  "network",
            "answer":  answer,
            "success": n["internet"],
            "data":    n,
        }

    def _unknown(self, question: str) -> dict:
        return {
            "intent":  "unknown",
            "answer":  f"Could not understand: '{question}'\n"
                       f"Try: 'is chrome open?', 'system status', "
                       f"'list processes', 'is file.txt present?'",
            "success": False,
            "data":    {},
        }
