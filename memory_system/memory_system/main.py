"""
Memory System — CLI

Commands:
  record   — add a task manually
  recall   — search for similar past tasks
  recent   — list recent tasks
  get <id> — show full task detail
  stats    — summary statistics
  delete <id>
  exit
"""
import sys
from memory_manager import MemoryManager

mm = MemoryManager()

DIVIDER = "─" * 60

def fmt_task(t: dict, detail: bool = False):
    status = "✅" if t["success"] else "❌"
    score  = f"quality={t['quality_score']:.2f}" if t.get("quality_score") else ""
    tags   = ", ".join(t.get("tags", [])[:6])
    lines  = [
        f"  [{t['id']}] {status} {t['goal']}",
        f"       category={t.get('category','-')} {score} retries={t.get('retries',0)} @ {t['created_at'][:19]}",
    ]
    if tags:
        lines.append(f"       tags: {tags}")
    if detail:
        if t.get("command"):  lines.append(f"       command: {t['command']}")
        if t.get("output"):   lines.append(f"       output:  {t['output'][:200]}")
        if t.get("error"):    lines.append(f"       error:   {t['error'][:200]}")
        steps = t.get("steps", [])
        if steps:
            lines.append(f"       steps ({len(steps)}):")
            for s in steps:
                icon = "✅" if s.get("success") else "❌"
                lines.append(f"         {icon} {s.get('step_name','?')} — {s.get('action','')[:60]}")
    return "\n".join(lines)

def cmd_record():
    print("Enter task details (press Enter to skip optional fields):")
    goal     = input("  Goal         : ").strip()
    command  = input("  Command      : ").strip()
    category = input("  Category (WEB_AGENT/PC_AGENT/BOTH): ").strip().upper() or "PC_AGENT"
    success  = input("  Success? (y/n): ").strip().lower() == "y"
    quality  = float(input("  Quality (0-1) : ").strip() or "1.0")
    retries  = int(input("  Retries       : ").strip() or "0")
    output   = input("  Output        : ").strip()
    error    = input("  Error         : ").strip()

    tid = mm.record(
        goal=goal, command=command, category=category,
        success=success, quality_score=quality,
        retries=retries, output=output, error=error,
    )
    print(f"\n  ✅ Saved as task #{tid}\n")

def cmd_recall():
    query = input("  Search query: ").strip()
    if not query: return
    results = mm.recall(query)
    if not results:
        print("  No similar tasks found.\n")
        return
    print(f"\n  Found {len(results)} similar task(s):\n")
    for t in results:
        match = t.get("_match_score", 0)
        print(fmt_task(t))
        print(f"       match_score={match}")
        print()

def cmd_recent():
    n = input("  How many? [10]: ").strip()
    n = int(n) if n.isdigit() else 10
    tasks = mm.recent(n)
    if not tasks:
        print("  No tasks recorded yet.\n")
        return
    print(f"\n  Last {len(tasks)} tasks:\n")
    for t in tasks:
        print(fmt_task(t))
    print()

def cmd_get(task_id_str: str):
    try:
        tid = int(task_id_str)
    except ValueError:
        print("  Invalid ID.\n"); return
    t = mm.get(tid)
    if not t:
        print(f"  Task {tid} not found.\n"); return
    print(f"\n{DIVIDER}")
    print(fmt_task(t, detail=True))
    print(f"{DIVIDER}\n")

def cmd_stats():
    s = mm.stats()
    total = s.get("total", 0)
    if total == 0:
        print("  No tasks recorded yet.\n"); return
    rate = (s["passed"] / total * 100) if total else 0
    print(f"\n{DIVIDER}")
    print(f"  Total tasks   : {total}")
    print(f"  Passed        : {s['passed']}  ({rate:.0f}%)")
    print(f"  Failed        : {s['failed']}")
    print(f"  Avg quality   : {s['avg_quality']}")
    print(f"  Avg retries   : {s['avg_retries']}")
    print(f"  Avg duration  : {s['avg_duration']}s")
    if s.get("by_category"):
        print(f"  By category:")
        for c in s["by_category"]:
            print(f"    {c['category']:12} — {c['count']} tasks, {c['passed']} passed")
    print(f"{DIVIDER}\n")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo(); return

    print("Memory System — Interactive\n")
    print("Commands: record | recall | recent | get <id> | stats | delete <id> | exit\n")
    while True:
        try:
            raw = input(">> ").strip()
            if not raw: continue
            parts = raw.split()
            cmd   = parts[0].lower()

            if cmd in ("exit", "quit"):      break
            elif cmd == "record":             cmd_record()
            elif cmd == "recall":             cmd_recall()
            elif cmd == "recent":             cmd_recent()
            elif cmd == "stats":              cmd_stats()
            elif cmd == "get"   and len(parts) > 1: cmd_get(parts[1])
            elif cmd == "delete"and len(parts) > 1:
                ok = mm.delete(int(parts[1]))
                print(f"  {'Deleted' if ok else 'Not found'}.\n")
            else:
                print("  Unknown command.\n")
        except KeyboardInterrupt:
            break

def run_demo():
    print("── Running demo ──\n")
    mm.start_task("open notepad")
    t1 = mm.record(goal="open notepad", command="open notepad", category="PC_AGENT",
                   success=True, quality_score=1.0, retries=0, output="notepad.exe launched",
                   steps=[{"name":"Launch app","action":"notepad.exe","success":True,"output":"OK","error":""}])

    mm.start_task("what is Python")
    t2 = mm.record(goal="what is Python", command="search Python language", category="WEB_AGENT",
                   success=True, quality_score=0.87, retries=1, output="Python is a programming language...",
                   steps=[{"name":"Search","action":"duckduckgo","success":True,"output":"5 results","error":""}])

    mm.start_task("create report.txt")
    t3 = mm.record(goal="create report.txt", command="create file report.txt", category="PC_AGENT",
                   success=False, quality_score=0.0, retries=3, error="Permission denied",
                   steps=[{"name":"Create file","action":"file_create","success":False,"output":"","error":"Permission denied"}])

    mm.start_task("search AI news and open browser")
    t4 = mm.record(goal="search AI news and open browser", command="search AI news open chrome",
                   category="BOTH", success=True, quality_score=0.92, retries=0)

    print(f"\nSaved tasks: {t1}, {t2}, {t3}, {t4}")

    print("\n── Recent tasks ──")
    for t in mm.recent(4):
        print(fmt_task(t))

    print("\n── Recall: 'open application' ──")
    for t in mm.recall("open application"):
        print(fmt_task(t))

    print("\n── Stats ──")
    cmd_stats()

if __name__ == "__main__":
    main()
