"""
Risk rules — defines CRITICAL / HIGH / MEDIUM risk patterns.
Safe commands pass through automatically.

Risk levels:
  CRITICAL  → always block or require strong confirmation + reason
  HIGH      → require explicit "yes" confirmation
  MEDIUM    → warn + confirm
  SAFE      → auto-allow
"""

from dataclasses import dataclass

@dataclass
class RiskRule:
    pattern:     str      # regex pattern (case-insensitive)
    level:       str      # CRITICAL | HIGH | MEDIUM
    description: str      # human explanation of the danger
    examples:    list     # example commands that match


RULES = [

    # ── CRITICAL ──────────────────────────────────────────────
    RiskRule(
        pattern     = r"\b(format\s+(c:|d:|e:|f:|/dev/sd))",
        level       = "CRITICAL",
        description = "Formats a drive — permanently destroys ALL data on it.",
        examples    = ["format c:", "format /dev/sda"],
    ),
    RiskRule(
        pattern     = r"\b(rm\s+-rf\s*/|rmdir\s*/s\s*/q\s*[a-z]:[\\/]?$|del\s+/[sf].*\*)",
        level       = "CRITICAL",
        description = "Recursive delete of root or system directory — catastrophic data loss.",
        examples    = ["rm -rf /", "rmdir /s /q C:\\"],
    ),
    RiskRule(
        pattern     = r"\b(bcdedit|bootrec|diskpart)\b",
        level       = "CRITICAL",
        description = "Modifies boot configuration or disk partitions — can make system unbootable.",
        examples    = ["bcdedit /delete", "diskpart"],
    ),
    RiskRule(
        pattern     = r"\breg\s+(delete|add|import)\b",
        level       = "CRITICAL",
        description = "Modifies the Windows registry — can break system or applications.",
        examples    = ["reg delete HKLM\\...", "reg add HKCU\\..."],
    ),

    # ── HIGH ──────────────────────────────────────────────────
    RiskRule(
        pattern     = r"\b(shutdown|poweroff|power\s*off)\b",
        level       = "HIGH",
        description = "Shuts down the computer — all unsaved work will be lost.",
        examples    = ["shutdown /s /t 0", "poweroff"],
    ),
    RiskRule(
        pattern     = r"\b(restart|reboot)\b",
        level       = "HIGH",
        description = "Restarts the computer — all unsaved work will be lost.",
        examples    = ["shutdown /r /t 0", "reboot"],
    ),
    RiskRule(
        pattern     = r"\b(taskkill|kill\s+-9|pkill)\b",
        level       = "HIGH",
        description = "Force-kills a process — unsaved data in that app will be lost.",
        examples    = ["taskkill /f /im chrome.exe", "kill -9 1234"],
    ),
    RiskRule(
        pattern     = r"\b(del|delete|remove|erase)\b.+\.(exe|dll|sys|bat|cmd|ps1|sh)\b",
        level       = "HIGH",
        description = "Deletes an executable or system file — may break software.",
        examples    = ["del myapp.exe", "delete setup.dll"],
    ),
    RiskRule(
        pattern     = r"\b(del|delete|rm)\b.+\*",
        level       = "HIGH",
        description = "Wildcard delete — deletes multiple files at once.",
        examples    = ["del *.txt", "rm -rf ./logs/*"],
    ),
    RiskRule(
        pattern     = r"\bnetsh\b",
        level       = "HIGH",
        description = "Modifies network configuration — can disrupt connectivity.",
        examples    = ["netsh interface set interface"],
    ),
    RiskRule(
        pattern     = r"\bsfc\s*/scannow\b",
        level       = "HIGH",
        description = "System File Checker — scans and replaces system files.",
        examples    = ["sfc /scannow"],
    ),
    RiskRule(
        pattern     = r"\bcipher\s+/w\b",
        level       = "HIGH",
        description = "Securely wipes free disk space — irreversible.",
        examples    = ["cipher /w:C:\\"],
    ),

    # ── MEDIUM ────────────────────────────────────────────────
    RiskRule(
        pattern     = r"\b(del|delete|remove|rm)\b(?!.*\*).+\.(txt|csv|log|json|xml|pdf|docx?|xlsx?)\b",
        level       = "MEDIUM",
        description = "Deletes a data file — this cannot be undone.",
        examples    = ["delete report.txt", "rm data.csv"],
    ),
    RiskRule(
        pattern     = r"\b(rmdir|rd)\b",
        level       = "MEDIUM",
        description = "Removes a directory — contents will be deleted.",
        examples    = ["rmdir /s old_folder", "rd backup"],
    ),
    RiskRule(
        pattern     = r"\bsc\s+(stop|delete|create|config)\b",
        level       = "MEDIUM",
        description = "Modifies a Windows service — may affect system stability.",
        examples    = ["sc stop wuauserv", "sc delete myservice"],
    ),
    RiskRule(
        pattern     = r"\bat\b|\bschtasks\b",
        level       = "MEDIUM",
        description = "Schedules a system task — will run automatically in background.",
        examples    = ["schtasks /create ...", "at 10:00 myscript.bat"],
    ),
]


# ── Safe whitelist ────────────────────────────────────────────
# Commands matching these patterns are always auto-approved.
SAFE_PATTERNS = [
    r"^(echo|print|type|cat)\b",              # read-only output
    r"^(dir|ls|pwd|cd|chdir)\b",              # navigation
    r"^(ipconfig|ifconfig|ping|tracert)\b",   # network info
    r"^(tasklist|ps\s+aux)\b",                # process list (read only)
    r"^(systeminfo|uname|ver|winver)\b",      # system info
    r"^(open|launch|start)\b",                # opening apps
    r"^(notepad|calc|mspaint|explorer)\b",    # common safe apps
    r"^(python|py)\b.+\.py\b",               # run python scripts
    r"^(mkdir|md)\b",                         # create directories (safe)
    r"^(copy|cp|xcopy|robocopy)\b",           # copy (not delete)
    r"^(move|mv|rename|ren)\b",               # rename/move (not delete)
]
