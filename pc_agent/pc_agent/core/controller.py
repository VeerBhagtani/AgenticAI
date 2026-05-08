"""
PCController: orchestrates parse → safety → execute → log.
"""

from pc_agent.core.parser import parse
from pc_agent.core.safety import is_risky, confirm
from pc_agent.core.actions import open_app, run_cmd, create_file, delete_file, list_dir


class PCController:
    def __init__(self, logger):
        self.logger = logger

        # Action dispatch table — add new actions here
        self._handlers = {
            "open_app":    self._open_app,
            "run_cmd":     self._run_cmd,
            "create_file": self._create_file,
            "delete_file": self._delete_file,
            "list_dir":    self._list_dir,
        }

    def execute(self, command: str) -> dict:
        self.logger.info(f"COMMAND: {command}")

        # 🔥 Generic open handler
        if command.lower().startswith("open "):
            app_name = command.lower().replace("open ", "").strip()
            return open_app(app_name)

        parsed = parse(command)
        action = parsed.get("action", "unknown")

        if action == "unknown":
            result = {"success": False, "message": f"Unknown command: '{command}'"}
            self.logger.warn(f"UNKNOWN: {command}")
            return result

    # ── Private Handlers ──────────────────────────────────────
    def _open_app(self, p):
        return open_app(p["target"])

    def _run_cmd(self, p):
        return run_cmd(p["command"])

    def _create_file(self, p):
        return create_file(p["path"], p.get("content", ""))

    def _delete_file(self, p):
        return delete_file(p["path"])

    def _list_dir(self, p):
        return list_dir(p["path"])