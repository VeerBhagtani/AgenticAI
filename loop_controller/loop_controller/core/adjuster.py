"""
Adjuster — modifies a step before retry based on failure context.
Add custom adjustment strategies here.
"""
from core.plan import Step

def adjust(step: Step, attempt: int, last_error: str) -> Step:
    """
    Returns a (possibly modified) Step for the next retry.
    Strategies applied in order — first match wins.
    """
    for strategy in STRATEGIES:
        result = strategy(step, attempt, last_error)
        if result is not None:
            return result
    return step  # no adjustment, retry as-is


# ── Adjustment Strategies ─────────────────────────────────────

def _extend_timeout(step: Step, attempt: int, error: str) -> Step | None:
    """If timed out, double the timeout."""
    if "timed out" in error.lower() or "timeout" in error.lower():
        new = _clone(step)
        new.timeout = step.timeout * 2
        return new
    return None

def _retry_with_force(step: Step, attempt: int, error: str) -> Step | None:
    """On 2nd+ retry of a cmd, prepend 'cmd /c' for robustness on Windows."""
    if attempt >= 2 and step.action_type == "cmd":
        action = str(step.action)
        if not action.startswith("cmd /c"):
            new = _clone(step)
            new.action = f"cmd /c {action}"
            return new
    return None

def _relax_check(step: Step, attempt: int, error: str) -> Step | None:
    """
    On 3rd+ retry, add a tolerance flag to check params.
    (Checked by checker — softens partial-match threshold.)
    """
    if attempt >= 3:
        new = _clone(step)
        new.check_params = {**step.check_params, "_relaxed": True}
        return new
    return None


STRATEGIES = [_extend_timeout, _retry_with_force, _relax_check]


def _clone(step: Step) -> Step:
    return Step(
        name         = step.name,
        action_type  = step.action_type,
        action       = step.action,
        check_type   = step.check_type,
        check_params = dict(step.check_params),
        timeout      = step.timeout,
        retryable    = step.retryable,
    )
