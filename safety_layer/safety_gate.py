"""
SafetyGate — the single entry point for all command safety checks.

Usage (interactive):
    gate = SafetyGate()
    result = gate.check("shutdown /s /t 0")
    if result["approved"]:
        execute_command(result["command"])

Usage (programmatic — from other agents):
    result = gate.check("delete report.txt", user_input="yes")
    result["approved"]  → True/False
    result["level"]     → SAFE | MEDIUM | HIGH | CRITICAL
    result["action"]    → ALLOW | CONFIRM | BLOCK

Result fields:
  command    str   — original command
  level      str   — SAFE / MEDIUM / HIGH / CRITICAL
  action     str   — ALLOW / CONFIRM / BLOCK
  approved   bool  — whether to proceed
  reason     str   — explanation
  auto       bool  — True if no human input was needed
"""
from core.scanner  import scan
from core.confirmer import confirm_interactive, confirm_programmatic
from core.logger   import Logger


class SafetyGate:
    def __init__(self):
        self.logger = Logger()

    def check(self, command: str, user_input: str = None) -> dict:
        """
        Main entry.
        - user_input=None  → interactive (prompts the user)
        - user_input=str   → programmatic (uses supplied string)
        """
        log    = self.logger
        result = scan(command)
        log.info(f"SCAN | level={result.level} action={result.action} | {command}")

        # ── SAFE: auto-allow ──────────────────────────────────
        if result.action == "ALLOW":
            log.allow(command, result.level)
            return self._ok(command, result.level, "Auto-allowed — safe command.", auto=True)

        # ── CRITICAL: require strong phrase OR block ──────────
        if result.level == "CRITICAL" and result.action == "BLOCK":
            if user_input is not None:
                conf = confirm_programmatic(result, user_input)
            else:
                conf = confirm_interactive(result)

            if conf["approved"]:
                log.confirmed(command, result.level)
                return self._ok(command, result.level, conf["reason"], auto=False)
            else:
                log.blocked(command, result.level, conf["reason"])
                return self._deny(command, result.level, conf["reason"])

        # ── HIGH / MEDIUM: confirm ────────────────────────────
        if result.action == "CONFIRM":
            if user_input is not None:
                conf = confirm_programmatic(result, user_input)
            else:
                conf = confirm_interactive(result)

            if conf["approved"]:
                log.confirmed(command, result.level)
                return self._ok(command, result.level, conf["reason"], auto=False)
            else:
                log.rejected(command, result.level, conf["reason"])
                return self._deny(command, result.level, conf["reason"])

        # Fallback
        return self._deny(command, result.level, "Unknown action — blocked by default.")

    # ── Helpers ───────────────────────────────────────────────

    def _ok(self, cmd, level, reason, auto):
        return {"command": cmd, "level": level, "action": "ALLOW",
                "approved": True,  "reason": reason, "auto": auto}

    def _deny(self, cmd, level, reason):
        return {"command": cmd, "level": level, "action": "DENY",
                "approved": False, "reason": reason, "auto": False}

    # ── Batch check (for loop_controller) ────────────────────

    def check_all(self, commands: list[str], auto_confirm_medium: bool = False) -> list[dict]:
        """
        Check a list of commands.
        auto_confirm_medium=True skips confirmation for MEDIUM risk.
        """
        results = []
        for cmd in commands:
            scan_r = scan(cmd)
            if scan_r.level == "MEDIUM" and auto_confirm_medium:
                results.append(self._ok(cmd, "MEDIUM", "Auto-confirmed (medium).", auto=True))
            else:
                results.append(self.check(cmd))
        return results
