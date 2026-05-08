"""
Scanner — matches a command against risk rules and safe whitelist.
Returns a ScanResult with level, matched rule, and recommendation.
"""
import re
from core.rules import RULES, SAFE_PATTERNS
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScanResult:
    command:     str
    level:       str            # SAFE | MEDIUM | HIGH | CRITICAL
    auto_allow:  bool
    rule:        object         # matched RiskRule or None
    reason:      str
    action:      str            # ALLOW | CONFIRM | BLOCK


def scan(command: str) -> ScanResult:
    cmd = command.strip()

    # ── 1. Whitelist check (auto-allow) ───────────────────────
    for pat in SAFE_PATTERNS:
        if re.match(pat, cmd, re.IGNORECASE):
            return ScanResult(
                command    = cmd,
                level      = "SAFE",
                auto_allow = True,
                rule       = None,
                reason     = "Matches safe command whitelist.",
                action     = "ALLOW",
            )

    # ── 2. Risk rule scan ─────────────────────────────────────
    for rule in RULES:
        if re.search(rule.pattern, cmd, re.IGNORECASE):
            auto  = False
            action = "CONFIRM" if rule.level in ("MEDIUM", "HIGH") else "BLOCK"
            return ScanResult(
                command    = cmd,
                level      = rule.level,
                auto_allow = auto,
                rule       = rule,
                reason     = rule.description,
                action     = action,
            )

    # ── 3. Unknown — allow with low-key notice ────────────────
    return ScanResult(
        command    = cmd,
        level      = "SAFE",
        auto_allow = True,
        rule       = None,
        reason     = "No risk patterns detected.",
        action     = "ALLOW",
    )
