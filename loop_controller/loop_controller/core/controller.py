"""
LoopController — the main execution engine.

Flow per step:
  execute → check → if fail: adjust → retry (up to max_retries)
  
Final result:
  {
    "goal":         str,
    "success":      bool,
    "steps_passed": int,
    "steps_failed": int,
    "total_retries":int,
    "step_results": list,
    "summary":      str
  }
"""
import time
from plan import Plan, Step
from executor import execute
from checker import run_check
from adjuster import adjust
from logger import Logger


class LoopController:
    def __init__(self):
        self.logger = Logger()

    def run(self, plan: Plan) -> dict:
        log = self.logger
        log.section(f"GOAL: {plan.goal}")
        if plan.description:
            log.info(f"Description: {plan.description}")
        log.info(f"Steps: {len(plan.steps)} | Max retries per step: {plan.max_retries}")

        step_results  = []
        steps_passed  = 0
        steps_failed  = 0
        total_retries = 0
        overall_ok    = True

        for i, step in enumerate(plan.steps, 1):
            log.section(f"STEP {i}/{len(plan.steps)}: {step.name}")
            result = self._run_step(step, plan.max_retries, plan.retry_delay, i)
            step_results.append(result)
            total_retries += result["retries"]

            if result["success"]:
                steps_passed += 1
                log.success(f"Step {i} passed (quality={result['quality']:.2f})")
            else:
                steps_failed += 1
                overall_ok = False
                log.fail(f"Step {i} FAILED after {result['retries']} retries — {result['last_error']}")
                # Decide whether to abort or continue
                if not step.retryable:
                    log.error("Step is non-retryable and failed — aborting plan.")
                    break

        summary = self._build_summary(plan.goal, overall_ok, steps_passed, steps_failed, total_retries)
        log.section(summary)

        return {
            "goal":          plan.goal,
            "success":       overall_ok,
            "steps_passed":  steps_passed,
            "steps_failed":  steps_failed,
            "total_retries": total_retries,
            "step_results":  step_results,
            "summary":       summary,
        }

    # ── Internal ──────────────────────────────────────────────

    def _run_step(self, step: Step, max_retries: int, delay: float, step_num: int) -> dict:
        log      = self.logger
        attempt  = 0
        current  = step
        last_err = ""
        quality  = 0.0

        while attempt <= max_retries:
            if attempt > 0:
                log.retry(attempt, f"Retrying '{step.name}' (delay={delay}s)")
                time.sleep(delay)
                if step.retryable:
                    current = adjust(step, attempt, last_err)
                    if current is not step:
                        log.info(f"  Adjusted: timeout={current.timeout}s, action='{current.action}'")

            # ── Execute ───────────────────────────────────────
            log.info(f"  [{attempt+1}] Executing: type={current.action_type} action={str(current.action)[:80]}")
            exec_result = execute(current)
            log.info(f"  Exec result: success={exec_result['success']} output={exec_result['output'][:120]}")

            if exec_result["error"]:
                log.warn(f"  Exec error: {exec_result['error']}")
                last_err = exec_result["error"]

            # ── Check ─────────────────────────────────────────
            log.info(f"  [{attempt+1}] Checking: type={current.check_type} params={current.check_params}")
            check_result = run_check(current.check_type, current.check_params)
            quality      = check_result["quality"]
            log.info(f"  Check result: success={check_result['success']} quality={quality:.2f} — {check_result['message']}")

            if check_result["success"]:
                return {
                    "step":       step.name,
                    "success":    True,
                    "retries":    attempt,
                    "quality":    quality,
                    "last_error": "",
                }

            last_err = check_result["message"]
            attempt += 1

        return {
            "step":       step.name,
            "success":    False,
            "retries":    attempt - 1,
            "quality":    quality,
            "last_error": last_err,
        }

    def _build_summary(self, goal, success, passed, failed, retries) -> str:
        status = "COMPLETED ✅" if success else "FAILED ❌"
        return (
            f"Goal: {goal}\n"
            f"Status: {status}\n"
            f"Steps passed: {passed} | Steps failed: {failed} | Total retries: {retries}"
        )
