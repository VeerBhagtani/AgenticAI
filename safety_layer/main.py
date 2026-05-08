"""
Safety Layer — Entry Point

Usage:
  python main.py "echo hello"              # auto-allowed
  python main.py "shutdown /s /t 0"        # requires yes
  python main.py "format c:"               # critical — strong confirm
  python main.py                           # interactive mode
"""
import sys
from safety_gate import SafetyGate
from core.scanner import scan
from core.rules import LEVEL_ICONS

DIVIDER = "─" * 55

def print_result(cmd, r):
    icon = "✅" if r["approved"] else "🚫"
    auto = " (auto)" if r.get("auto") else ""
    print(f"\n{DIVIDER}")
    print(f"  Command  : {cmd}")
    print(f"  Level    : {LEVEL_ICONS.get(r['level'], r['level'])}")
    print(f"  Decision : {icon} {'APPROVED' if r['approved'] else 'DENIED'}{auto}")
    print(f"  Reason   : {r['reason']}")
    print(f"{DIVIDER}\n")

def preview(cmd):
    """Show risk level without executing."""
    r = scan(cmd)
    icon = LEVEL_ICONS.get(r.level, r.level)
    print(f"\n  {icon} | {cmd}")
    if r.rule:
        print(f"  ⚠  {r.reason}")
    else:
        print(f"  ✓  {r.reason}")
    print()

def main():
    gate = SafetyGate()

    if len(sys.argv) > 1:
        cmd    = " ".join(sys.argv[1:])
        result = gate.check(cmd)
        print_result(cmd, result)
        return

    print("Safety Layer — Interactive Mode")
    print("Commands: check | preview | demo | exit\n")

    while True:
        try:
            raw = input(">> ").strip()
            if not raw: continue
            if raw.lower() in ("exit", "quit"): break

            if raw.lower() == "demo":
                run_demo(gate)
                continue

            if raw.lower().startswith("preview "):
                preview(raw[8:].strip())
                continue

            # Default: run safety check on the whole input
            result = gate.check(raw)
            print_result(raw, result)

        except KeyboardInterrupt:
            break


def run_demo(gate: SafetyGate):
    """Show how different commands are classified without prompting."""
    demos = [
        # (command, expected_level, mock_user_input)
        ("echo Hello World",             "SAFE",     None),
        ("dir C:\\Users",                "SAFE",     None),
        ("ipconfig",                     "SAFE",     None),
        ("open notepad",                 "SAFE",     None),
        ("rmdir /s old_folder",          "MEDIUM",   "yes"),
        ("del report.txt",               "MEDIUM",   "y"),
        ("taskkill /f /im chrome.exe",   "HIGH",     "yes"),
        ("shutdown /s /t 0",             "HIGH",     "no"),       # user rejects
        ("reg delete HKLM\\Test",        "CRITICAL", "wrong"),    # wrong phrase
        ("format c:",                    "CRITICAL", "I understand the risk and confirm"),
    ]

    print(f"\n{'═'*55}")
    print("  SAFETY LAYER DEMO")
    print(f"{'═'*55}\n")

    for cmd, expected, mock_input in demos:
        result = gate.check(cmd, user_input=mock_input)
        icon   = "✅" if result["approved"] else "🚫"
        auto   = " [auto]" if result.get("auto") else ""
        level  = f"{LEVEL_ICONS.get(result['level'], result['level'])}"
        print(f"  {icon}{auto} [{level}]")
        print(f"     {cmd}")
        print(f"     → {result['reason']}")
        print()


if __name__ == "__main__":
    main()
