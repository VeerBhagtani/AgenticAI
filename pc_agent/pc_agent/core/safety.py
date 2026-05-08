"""
Safety module — flags risky commands and prompts confirmation.
"""

# Patterns that require user confirmation
RISKY_PATTERNS = [
    "del ", "delete ", "rmdir", "remove",
    "format", "shutdown", "restart", "taskkill",
    "reg delete", "reg add", "netsh", "cipher",
    "diskpart", "bcdedit", "sfc /scannow",
]

def is_risky(command: str) -> bool:
    cmd_lower = command.lower()
    return any(p in cmd_lower for p in RISKY_PATTERNS)

def confirm(command: str) -> bool:
    """Prompt user to confirm a risky command. Returns True if confirmed."""
    print(f"\n⚠️  Risky command detected: '{command}'")
    answer = input("   Confirm? (yes/no): ").strip().lower()
    return answer in ("yes", "y")
