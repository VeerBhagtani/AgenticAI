"""
Loop Controller — Entry Point

Usage:
  python main.py demo          # run all example plans
  python main.py demo file     # run file plan only
  python main.py demo cmd      # run cmd plan only
  python main.py demo python   # run python plan only
  python main.py               # interactive mode
"""
import sys
from core.controller import LoopController
from strategies.example_plans import plan_create_file, plan_run_and_verify, plan_python_task

DEMO_PLANS = {
    "file":   plan_create_file,
    "cmd":    plan_run_and_verify,
    "python": plan_python_task,
}

def print_result(r: dict):
    print("\n" + "="*60)
    print(f"  GOAL    : {r['goal']}")
    print(f"  STATUS  : {'✅ SUCCESS' if r['success'] else '❌ FAILED'}")
    print(f"  Passed  : {r['steps_passed']} / {r['steps_passed'] + r['steps_failed']} steps")
    print(f"  Retries : {r['total_retries']}")
    for i, s in enumerate(r['step_results'], 1):
        icon = "✅" if s['success'] else "❌"
        print(f"  Step {i}  : {icon} {s['step']} | quality={s['quality']:.2f} | retries={s['retries']}")
        if not s['success']:
            print(f"           ↳ {s['last_error']}")
    print("="*60 + "\n")

def run_demo(key=None):
    ctrl = LoopController()
    plans = {key: DEMO_PLANS[key]} if key else DEMO_PLANS
    for name, builder in plans.items():
        print(f"\n▶ Running demo plan: {name}")
        result = ctrl.run(builder())
        print_result(result)

def interactive():
    print("Loop Controller — Interactive Mode")
    print("Build a custom plan or run a demo.\n")
    print("Commands:")
    print("  demo               — run all demo plans")
    print("  demo <file|cmd|python> — run specific demo")
    print("  exit\n")
    while True:
        try:
            cmd = input(">> ").strip().lower()
            if not cmd: continue
            if cmd in ("exit", "quit"): break
            if cmd == "demo":
                run_demo()
            elif cmd.startswith("demo "):
                key = cmd.split(None, 1)[1]
                if key in DEMO_PLANS:
                    run_demo(key)
                else:
                    print(f"Unknown demo: {key}. Options: {list(DEMO_PLANS.keys())}")
            else:
                print("Unknown command.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "demo":
        key = args[1] if len(args) > 1 else None
        if key and key not in DEMO_PLANS:
            print(f"Unknown demo: {key}. Options: {list(DEMO_PLANS.keys())}")
        else:
            run_demo(key)
    else:
        interactive()
