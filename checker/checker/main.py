"""
Task Checker — Entry Point
Usage:
  python main.py                        # interactive menu
  python main.py check file C:/out.txt  # CLI mode
"""
import sys
from core.checker import TaskChecker

def print_result(r: dict):
    status = "✅ PASS" if r["success"] else "❌ FAIL"
    print(f"\n{status}")
    print(f"  Task type  : {r['task_type']}")
    print(f"  Rule result: {r['rule_result']}")
    print(f"  Quality    : {r['quality_score']:.2f} / 1.00")
    print(f"  Confidence : {r['confidence']:.2f} / 1.00")
    print(f"  Message    : {r['message']}")
    if r.get("details"):
        print(f"  Details    : {r['details']}")
    print()

def interactive():
    checker = TaskChecker()
    print("Task Checker — Interactive Mode")
    print("Commands:")
    print("  check file <path>")
    print("  check app <process_name>")
    print("  check output <expected_text> in <file_or_string>")
    print("  check cmd <command> expects <expected_output>")
    print("  exit\n")

    while True:
        try:
            raw = input(">> ").strip()
            if not raw: continue
            if raw.lower() in ("exit", "quit"): break

            parts = raw.split()
            if parts[0].lower() != "check" or len(parts) < 3:
                print("Usage: check <type> <args...>")
                continue

            task_type = parts[1].lower()

            if task_type == "file":
                result = checker.check("file", {"path": parts[2]})

            elif task_type == "app":
                result = checker.check("app", {"process": parts[2]})

            elif task_type == "output":
                # check output <text> in <source>
                try:
                    in_idx = [p.lower() for p in parts].index("in")
                    expected = " ".join(parts[2:in_idx])
                    source   = " ".join(parts[in_idx+1:])
                    result = checker.check("output", {"expected": expected, "source": source})
                except ValueError:
                    print("Usage: check output <text> in <file_or_string>")
                    continue

            elif task_type == "cmd":
                # check cmd <command> expects <text>
                try:
                    exp_idx = [p.lower() for p in parts].index("expects")
                    command  = " ".join(parts[2:exp_idx])
                    expected = " ".join(parts[exp_idx+1:])
                    result = checker.check("cmd", {"command": command, "expected": expected})
                except ValueError:
                    print("Usage: check cmd <command> expects <output>")
                    continue
            else:
                print(f"Unknown task type: {task_type}")
                continue

            print_result(result)

        except KeyboardInterrupt:
            break

def cli(args):
    checker = TaskChecker()
    if len(args) < 3:
        print("Usage: python main.py check <type> <args...>")
        return
    task_type = args[1].lower()
    arg = " ".join(args[2:])
    result = checker.check(task_type, {"path": arg, "process": arg, "source": arg, "expected": arg})
    print_result(result)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli(sys.argv[1:])
    else:
        interactive()
