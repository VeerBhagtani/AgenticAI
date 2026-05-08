"""
ORCHESTRATOR — main.py
Integrates all 8 modules into a single goal-driven pipeline.

Usage:
  python main.py "your goal here"
  python main.py                    # interactive mode

Flow:
  goal → decision → safety (PC only) → execute → check → retry? → memory
"""
import sys 
import os

# 🔥 Add project root to Python path (GLOBAL FIX)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR) 

import time
import logging
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# MODULE IMPORTS  — all via importlib to avoid name collisions
# (multiple modules share names like core.engine, core.controller)
# ─────────────────────────────────────────────────────────────
import importlib.util as _ilu
BASE = os.path.dirname(os.path.abspath(__file__))
def _load(alias, rel_path, root_rel):
    full = os.path.abspath(os.path.join(BASE, "..", "..", rel_path))
    root = os.path.dirname(os.path.abspath(full))
    root = os.path.dirname(os.path.abspath(full))

    # Clear stale 'core' so each module's core/ resolves fresh
    for key in list(sys.modules.keys()):
        if key == "core" or key.startswith("core."):
            del sys.modules[key]

    # Put this module's root first on sys.path
    if root in sys.path:
        sys.path.remove(root)
    sys.path.insert(0, root)

    spec = _ilu.spec_from_file_location(alias, full)
    mod  = _ilu.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod

# Decision module
_dm = _load("dm_engine", "decision_module/decision_module/core/engine.py", "decision_module")
DecisionEngine = _dm.DecisionEngine

# Web agent  — root is web_agent/ so "from agent.logger" resolves
_wa          = _load("wa_ctrl",       "web_agent/agent/controller.py",     "web_agent")
WebAgent     = _wa.WebAgent

# PC agent — load controller + logger separately (same root)
_pc_ctrl = _load("pc_controller", "pc_agent/pc_agent/core/controller.py", "pc_agent")
_pc_log = _load("pc_logger", "pc_agent/pc_agent/core/logger.py", "pc_agent")
PCController = _pc_ctrl.PCController
AgentLogger  = _pc_log.AgentLogger

# Checker
_chk = _load("chk_checker", "checker/checker/core/checker.py", "checker")
TaskChecker  = _chk.TaskChecker

# Loop controller
_lc = _load("lc_ctrl", "loop_controller/loop_controller/core/controller.py", "loop_controller")
_lp = _load("lc_plan", "loop_controller/loop_controller/core/plan.py", "loop_controller")

LoopController = _lc.LoopController
Plan = _lp.Plan
Step = _lp.Step

# Memory system
_mm          = _load("mm_manager",   "memory_system/memory_system/memory_manager.py",    "memory_system")
MemoryManager = _mm.MemoryManager

# Status module
_se          = _load("sm_engine",    "status_module/status_module/core/engine.py",       "status_module")
StatusEngine = _se.StatusEngine

# Safety layer
_sg          = _load("sg_gate",      "safety_layer/safety_gate.py",        "safety_layer")
SafetyGate   = _sg.SafetyGate


# ─────────────────────────────────────────────────────────────
# ORCHESTRATOR LOGGER
# ─────────────────────────────────────────────────────────────
LOG_DIR = os.path.join(BASE, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Prevent child module basicConfig() calls from adding duplicate console handlers
logging.root.handlers = []
logging.root.setLevel(logging.CRITICAL)   # silence root; orchestrator uses its own logger

def _setup_logger():
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    log = logging.getLogger("Orchestrator")
    log.setLevel(logging.INFO)
    log.propagate = False   # don't also send to root logger
    if not log.handlers:
        fh = logging.FileHandler(os.path.join(LOG_DIR, f"orchestrator_{ts}.log"))
        sh = logging.StreamHandler()
        fh.setFormatter(logging.Formatter(fmt))
        sh.setFormatter(logging.Formatter(fmt))
        log.addHandler(fh)
        log.addHandler(sh)
    # Silence child module loggers so they don't double-print to console
    for name in ["PCAgent", "WebAgent", "Checker", "LoopController",
                 "MemorySystem", "StatusModule", "SafetyLayer",
                 "DecisionModule", "Memory", "Checker"]:
        logging.getLogger(name).propagate = False
    return log

log = _setup_logger()

DIVIDER  = "─" * 60
DIVIDER2 = "═" * 60


# ─────────────────────────────────────────────────────────────
# STEP HELPERS
# ─────────────────────────────────────────────────────────────

def step(n, label):
    log.info(f"\n{DIVIDER}\n  STEP {n}: {label}\n{DIVIDER}")


def banner(title):
    log.info(f"\n{DIVIDER2}\n  {title}\n{DIVIDER2}")


# ─────────────────────────────────────────────────────────────
# MODULE INSTANCES  (created once, reused)
# ─────────────────────────────────────────────────────────────
decision_engine = DecisionEngine()
web_agent       = WebAgent()
pc_logger       = AgentLogger()
pc_agent        = PCController(pc_logger)
task_checker    = TaskChecker()
loop_ctrl       = LoopController()
memory          = MemoryManager()
status_engine   = StatusEngine()
safety_gate     = SafetyGate()


# ─────────────────────────────────────────────────────────────
# CORE PIPELINE
# ─────────────────────────────────────────────────────────────

def run(goal: str):
    banner(f"ORCHESTRATOR  |  GOAL: {goal}")
    memory.start_task(goal)
    start_time = time.time()
    actions_taken = []
    task_id       = None

    try:
        # ── STEP 1: RECALL similar past tasks ─────────────────
        step(1, "MEMORY RECALL — checking past similar tasks")
        similar = memory.recall(goal, limit=3)
        if similar:
            log.info(f"  Found {len(similar)} similar past task(s):")
            for t in similar:
                status = "✅" if t["success"] else "❌"
                log.info(f"    [{t['id']}] {status} {t['goal']} | quality={t.get('quality_score',0):.2f}")
        else:
            log.info("  No similar past tasks found — fresh start.")

        # ── STEP 2: DECISION ──────────────────────────────────
        step(2, "DECISION — routing goal to correct agent")
        decision = decision_engine.decide(goal)
        category   = decision["category"]
        confidence = decision["confidence"]
        log.info(f"  Category   : {category}")
        log.info(f"  Agent      : {decision['agent']}")
        log.info(f"  Confidence : {confidence:.0%}")
        log.info(f"  Reasoning  : {decision['reasoning']}")
        actions_taken.append(f"decision:{category}:{confidence:.2f}")

        # ── STEP 3: STATUS CHECK (for PC or BOTH) ─────────────
        if category in ("PC_AGENT", "BOTH"):
            step(3, "STATUS CHECK — verifying system state")
            sys_status = status_engine.query("system status")
            log.info(f"  {sys_status['answer']}")
            actions_taken.append("status:system_check")

        # ── STEP 4: EXECUTE ───────────────────────────────────
        step(4, f"EXECUTE — running {category}")

        exec_result   = {"success": False, "output": "", "quality_score": 0.0}
        check_result  = {"success": False, "quality_score": 0.0, "verdict": "NOT CHECKED"}

        # ── WEB AGENT ─────────────────────────────────────────
        if category == "WEB_AGENT":
            exec_result = _run_web_agent(goal)
            actions_taken.append(f"web_agent:search:{goal[:40]}")

        # ── PC AGENT ──────────────────────────────────────────
        elif category == "PC_AGENT":
            exec_result = _run_pc_agent(goal, actions_taken)

        # ── BOTH ──────────────────────────────────────────────
        elif category == "BOTH":
            log.info("  Running Web Agent first to gather info...")
            web_result  = _run_web_agent(goal)
            actions_taken.append(f"web_agent:search:{goal[:40]}")

            log.info("  Passing web result to PC Agent...")
            pc_command  = decision["suggested_params"].get("command", goal)
            exec_result = _run_pc_agent(pc_command, actions_taken)
            # Merge outputs
            exec_result["output"] = (
                "[WEB] " + web_result.get("output", "")[:300] + "\n" +
                "[PC]  " + exec_result.get("output", "")[:300]
            )

        # ── UNKNOWN ───────────────────────────────────────────
        else:
            log.warning(f"  Unknown category '{category}' — cannot execute.")
            exec_result = {"success": False, "output": "Unknown category.", "quality_score": 0.0}

        log.info(f"  Execution success: {exec_result['success']}")
        log.info(f"  Output preview  : {str(exec_result.get('output',''))[:200]}")

        # ── STEP 5: CHECK RESULT ──────────────────────────────
        step(5, "CHECKER — verifying result quality")
        check_result = _check_result(goal, category, exec_result)
        log.info(f"  Check success  : {check_result['success']}")
        log.info(f"  Quality score  : {check_result['quality_score']:.2f}")
        log.info(f"  Verdict        : {check_result.get('verdict','')}")
        actions_taken.append(f"check:{check_result['success']}:q={check_result['quality_score']:.2f}")

        # ── STEP 6: RETRY via LOOP CONTROLLER if needed ───────
        final_result = check_result
        if not check_result["success"] and category in ("PC_AGENT", "BOTH"):
            step(6, "LOOP CONTROLLER — retrying failed PC task")
            loop_result = _retry_with_loop(goal, exec_result, actions_taken)
            if loop_result["success"]:
                final_result = {
                    "success":       True,
                    "quality_score": 0.8,
                    "verdict":       "RECOVERED via loop controller",
                }
                log.info("  ✅ Loop controller recovered the task.")
            else:
                log.warning("  ❌ Loop controller exhausted retries — task failed.")
            actions_taken.append(f"loop:retries={loop_result.get('total_retries',0)}")
        else:
            step(6, "LOOP CONTROLLER — skipped (task succeeded or not applicable)")

        # ── STEP 7: MEMORY STORE ──────────────────────────────
        step(7, "MEMORY — storing result")
        duration = round(time.time() - start_time, 2)
        task_id  = memory.record(
            goal          = goal,
            command       = goal,
            category      = category,
            success       = final_result["success"],
            quality_score = final_result["quality_score"],
            retries       = 0,
            output        = str(exec_result.get("output", ""))[:500],
            error         = "" if final_result["success"] else check_result.get("message", ""),
            steps         = [{"name": a, "action": a, "success": final_result["success"],
                              "output": "", "error": ""} for a in actions_taken],
        )
        log.info(f"  Saved as task #{task_id} (duration={duration}s)")

        # ── FINAL REPORT ──────────────────────────────────────
        _print_report(goal, category, final_result, task_id, duration, actions_taken)

        return final_result

    except Exception as e:
        log.error(f"ORCHESTRATOR ERROR: {e}")
        import traceback; traceback.print_exc()
        if task_id is None:
            memory.record(goal=goal, command=goal, success=False,
                          error=str(e), quality_score=0.0)
        return {"success": False, "quality_score": 0.0, "verdict": f"Error: {e}"}


# ─────────────────────────────────────────────────────────────
# EXECUTION HELPERS
# ─────────────────────────────────────────────────────────────

def _run_web_agent(goal: str) -> dict:
    log.info(f"  [WEB] Searching: {goal}")
    try:
        output = web_agent.run(goal)
        success = bool(output) and "❌" not in output[:10]
        return {"success": success, "output": output, "quality_score": 0.85 if success else 0.0}
    except Exception as e:
        log.error(f"  [WEB] Error: {e}")
        return {"success": False, "output": "", "quality_score": 0.0, "error": str(e)}


def _run_pc_agent(command: str, actions_taken: list) -> dict:
    log.info(f"  [PC] Command: {command}")

    # ── Safety gate ───────────────────────────────────────────
    log.info(f"  [SAFETY] Scanning: {command}")
    safety = safety_gate.check(command)
    actions_taken.append(f"safety:{safety['level']}:{safety['action']}")

    log.info(f"  [SAFETY] Level={safety['level']} | Approved={safety['approved']}")

    if not safety["approved"]:
        log.warning(f"  [SAFETY] BLOCKED: {safety['reason']}")
        return {
            "success":       False,
            "output":        f"Blocked by safety layer: {safety['reason']}",
            "quality_score": 0.0,
        }

    # ── Execute ───────────────────────────────────────────────
    try:
        result = pc_agent.execute(command)
        success = result.get("success", False)
        msg     = result.get("message", "")
        log.info(f"  [PC] Result: success={success} | {msg[:100]}")
        return {
            "success":       success,
            "output":        msg,
            "quality_score": 1.0 if success else 0.0,
        }
    except Exception as e:
        log.error(f"  [PC] Error: {e}")
        return {"success": False, "output": str(e), "quality_score": 0.0}


# ─────────────────────────────────────────────────────────────
# CHECKER HELPER
# ─────────────────────────────────────────────────────────────

def _check_result(goal: str, category: str, exec_result: dict) -> dict:
    """
    Pick the most appropriate checker type based on category and output.
    """
    output = exec_result.get("output", "")

    if not exec_result.get("success"):
        return {
            "success":       False,
            "quality_score": 0.0,
            "verdict":       "FAILED",
            "message":       "Execution did not succeed.",
        }

    try:
        if category == "WEB_AGENT":
            # Check that output contains words from the goal
            check = task_checker.check("output", {
                "expected": " ".join(goal.split()[:4]),
                "source":   output,
            })
        else:
            # For PC/BOTH: check output string is non-empty and positive
            check = task_checker.check("output", {
                "expected": "success" if "success" in output.lower() else goal.split()[0],
                "source":   output,
            })

        return {
            "success":       check["success"],
            "quality_score": check.get("quality_score", exec_result.get("quality_score", 0.5)),
            "verdict":       check.get("verdict", ""),
            "message":       check.get("message", ""),
        }
    except Exception as e:
        log.warning(f"  Checker error: {e} — using exec result directly")
        return {
            "success":       exec_result.get("success", False),
            "quality_score": exec_result.get("quality_score", 0.5),
            "verdict":       "CHECK_ERROR",
            "message":       str(e),
        }


# ─────────────────────────────────────────────────────────────
# LOOP CONTROLLER HELPER
# ─────────────────────────────────────────────────────────────

def _retry_with_loop(goal: str, exec_result: dict, actions_taken: list) -> dict:
    """Build a minimal Plan and run it through the loop controller."""
    log.info(f"  [LOOP] Building retry plan for: {goal}")

    # Safety-check the retry command first
    safety = safety_gate.check(goal)
    if not safety["approved"]:
        log.warning(f"  [LOOP] Safety blocked retry: {safety['reason']}")
        return {"success": False, "total_retries": 0}

    plan = Plan(
        goal        = goal,
        max_retries = 3,
        retry_delay = 1.0,
        steps = [
            Step(
                name         = f"Retry: {goal[:40]}",
                action_type  = "cmd",
                action       = goal,
                check_type   = "output",
                check_params = {
                    "expected": goal.split()[0],
                    "source":   exec_result.get("output", ""),
                },
            )
        ]
    )

    try:
        result = loop_ctrl.run(plan)
        return result
    except Exception as e:
        log.error(f"  [LOOP] Error: {e}")
        return {"success": False, "total_retries": 0}


# ─────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────

def _print_report(goal, category, result, task_id, duration, actions):
    status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
    q      = result.get("quality_score", 0.0)
    bar    = "█" * int(q * 20) + "░" * (20 - int(q * 20))

    log.info(f"\n{DIVIDER2}")
    log.info(f"  ORCHESTRATOR FINAL REPORT")
    log.info(f"{DIVIDER2}")
    log.info(f"  Goal          : {goal}")
    log.info(f"  Status        : {status}")
    log.info(f"  Category      : {category}")
    log.info(f"  Quality       : [{bar}] {q:.0%}")
    log.info(f"  Duration      : {duration}s")
    log.info(f"  Memory task # : {task_id}")
    log.info(f"  Verdict       : {result.get('verdict','')}")
    log.info(f"  Actions taken :")
    for i, a in enumerate(actions, 1):
        log.info(f"    {i}. {a}")
    log.info(DIVIDER2)


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        goal = " ".join(sys.argv[1:])
        run(goal)
    else:
        print(f"\n{'═'*60}")
        print("  ORCHESTRATOR — Interactive Mode")
        print("  All 8 modules active. Type a goal and press Enter.")
        print(f"{'═'*60}\n")
        print("  Examples:")
        print('    "open notepad"')
        print('    "what is quantum computing"')
        print('    "create file C:/test.txt"')
        print('    "latest AI news"')
        print()
        while True:
            try:
                goal = input("Goal >> ").strip()
                if not goal:
                    continue
                if goal.lower() in ("exit", "quit"):
                    break
                run(goal)
                print()
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()
