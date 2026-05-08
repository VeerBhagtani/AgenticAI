"""
Decision Module — Entry Point

Usage:
  python main.py "open notepad"
  python main.py "what is photosynthesis"
  python main.py                       # interactive
"""
import sys
from core.engine import DecisionEngine

DIVIDER = "─" * 55

def print_decision(d: dict):
    cat_icons = {"WEB_AGENT": "🌐", "PC_AGENT": "💻", "BOTH": "🔗", "UNKNOWN": "❓"}
    icon = cat_icons.get(d["category"], "?")
    bar  = "█" * int(d["confidence"] * 20) + "░" * (20 - int(d["confidence"] * 20))

    print(f"\n{DIVIDER}")
    print(f"  GOAL       : {d['goal']}")
    print(f"  DECISION   : {icon}  {d['category']}")
    print(f"  AGENT      : {d['agent']}")
    print(f"  CONFIDENCE : [{bar}] {d['confidence']:.0%}")
    print(f"  REASONING  : {d['reasoning']}")
    print(f"\n  SUGGESTED PLAN:")
    for step in d["suggested_steps"]:
        print(f"    {step}")
    if d["suggested_params"]:
        print(f"\n  PARAMS     : {d['suggested_params']}")
    print(f"{DIVIDER}\n")

def main():
    engine = DecisionEngine()

    if len(sys.argv) > 1:
        goal   = " ".join(sys.argv[1:])
        result = engine.decide(goal)
        print_decision(result)
        return

    print("Decision Module — Interactive Mode")
    print("Type a goal and get routed to the right agent.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            goal = input("Goal >> ").strip()
            if not goal: continue
            if goal.lower() in ("exit", "quit"): break
            result = engine.decide(goal)
            print_decision(result)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
