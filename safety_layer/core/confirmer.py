"""
Confirmer — interactive and programmatic confirmation flows.
"""
import sys

LEVEL_ICONS = {
    "CRITICAL": "🔴 CRITICAL",
    "HIGH":     "🟠 HIGH",
    "MEDIUM":   "🟡 MEDIUM",
    "SAFE":     "🟢 SAFE",
}

def confirm_interactive(scan_result) -> dict:
    """
    Shows risk info and prompts the user.
    Returns {"approved": bool, "reason": str}
    """
    level = scan_result.level
    icon  = LEVEL_ICONS.get(level, level)
    cmd   = scan_result.command
    rule  = scan_result.rule

    print(f"\n{'─'*55}")
    print(f"  ⚠️  SAFETY CHECK — {icon}")
    print(f"{'─'*55}")
    print(f"  Command : {cmd}")
    if rule:
        print(f"  Risk    : {rule.description}")
        if rule.examples:
            print(f"  Example : {rule.examples[0]}")
    print(f"{'─'*55}")

    if level == "CRITICAL":
        print("  ❗ This command is CRITICAL risk.")
        print("  Type the exact phrase to confirm:")
        print('  → "I understand the risk and confirm"')
        answer = input("  >> ").strip()
        approved = answer == "I understand the risk and confirm"
        reason   = "User confirmed critical action." if approved else "User did not confirm critical action."

    elif level == "HIGH":
        print("  Type 'yes' to proceed or anything else to cancel:")
        answer   = input("  >> ").strip().lower()
        approved = answer == "yes"
        reason   = "User approved." if approved else f"User typed '{answer}' — rejected."

    else:  # MEDIUM
        print("  Type 'yes' or 'y' to proceed:")
        answer   = input("  >> ").strip().lower()
        approved = answer in ("yes", "y")
        reason   = "User approved." if approved else "User cancelled."

    print(f"{'─'*55}")
    return {"approved": approved, "reason": reason}


def confirm_programmatic(scan_result, user_input: str) -> dict:
    """
    Non-interactive version — takes pre-supplied user_input.
    Used when calling from other agents (loop_controller, pc_agent).
    """
    level = scan_result.level
    ui    = user_input.strip()

    if level == "CRITICAL":
        approved = ui == "I understand the risk and confirm"
    elif level == "HIGH":
        approved = ui.lower() == "yes"
    else:  # MEDIUM
        approved = ui.lower() in ("yes", "y")

    return {
        "approved": approved,
        "reason": "Approved via programmatic input." if approved else "Rejected via programmatic input."
    }
