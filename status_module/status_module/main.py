"""
System Status Module — Entry Point

Usage:
  python main.py "is chrome open?"
  python main.py "system status"
  python main.py                    # interactive
"""
import sys
from core.engine import StatusEngine

DIVIDER = "─" * 55

def print_result(r: dict):
    print(f"\n{DIVIDER}")
    print(f"  Q: {r.get('_query','')}")
    print(f"\n{r['answer']}")
    print(f"{DIVIDER}\n")

def main():
    engine = StatusEngine()

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        result   = engine.query(question)
        result["_query"] = question
        print_result(result)
        return

    print("System Status Module")
    print("Ask anything about your system state.\n")
    print("Examples:")
    print("  is chrome open?")
    print("  is notepad running?")
    print("  is C:/Users/file.txt present?")
    print("  system status")
    print("  list all processes")
    print("  what windows are open?")
    print("  internet status")
    print("  exit\n")

    while True:
        try:
            q = input(">> ").strip()
            if not q: continue
            if q.lower() in ("exit", "quit"): break
            result = engine.query(q)
            result["_query"] = q
            print_result(result)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
