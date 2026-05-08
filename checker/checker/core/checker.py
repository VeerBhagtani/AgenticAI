"""
TaskChecker — routes task type to correct rule, then quality-scores result.
"""

import os
import importlib.util
import sys

# ✅ DEFINE FIRST (VERY IMPORTANT)
current_dir = os.path.dirname(os.path.abspath(__file__))


# 🔥 Load logger.py and quality.py manually

# --- Logger ---
logger_path = os.path.join(current_dir, "logger.py")
logger_path = os.path.abspath(logger_path)

spec_logger = importlib.util.spec_from_file_location("logger", logger_path)
logger_module = importlib.util.module_from_spec(spec_logger)
spec_logger.loader.exec_module(logger_module)

Logger = logger_module.Logger


# --- Quality ---
quality_path = os.path.join(current_dir, "quality.py")
quality_path = os.path.abspath(quality_path)

spec_quality = importlib.util.spec_from_file_location("quality", quality_path)
quality_module = importlib.util.module_from_spec(spec_quality)
spec_quality.loader.exec_module(quality_module)

assess = quality_module.assess


# 🔥 Load rules modules correctly (based on folder structure)

rules_dir = os.path.join(current_dir, "..", "rules")
rules_dir = os.path.abspath(rules_dir)


if rules_dir not in sys.path:
    sys.path.insert(0, rules_dir)

# 🔥 Load rule modules dynamically (no assumptions)

def load_rule_module(name):
    path = os.path.join(rules_dir, f"{name}.py")
    path = os.path.abspath(path)

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


file_rule = load_rule_module("file_rule")
app_rule = load_rule_module("app_rule")
cmd_rule = load_rule_module("cmd_rule")
output_rule = load_rule_module("output_rule")


RULE_MAP = {
    "file": file_rule,
    "app": app_rule,
    "output": output_rule,
    "cmd": cmd_rule,
}

class TaskChecker:
    def __init__(self):
        self.logger = Logger()

    def check(self, task_type: str, params: dict) -> dict:
        log = self.logger
        log.info(f"CHECK | type={task_type} | params={params}")

        task_type = task_type.lower().strip()

        # ── Route to rule ─────────────────────────────────────
        rule_module = RULE_MAP.get(task_type)
        if not rule_module:
            supported = list(RULE_MAP.keys())
            log.error(f"Unknown task type: {task_type}")
            return self._unknown(task_type, supported)

        # ── Run rule ──────────────────────────────────────────
        try:
            rule_result = rule_module.check(params)
        except Exception as e:
            log.error(f"Rule crashed: {e}")
            rule_result = {
                "success": False, "rule_name": task_type,
                "quality": 0.0, "message": f"Rule error: {e}", "details": ""
            }

        # ── Quality assessment ────────────────────────────────
        quality_data = assess(rule_result, task_type)

        # ── Assemble final result ─────────────────────────────
        final = {
            "success":        rule_result["success"],
            "task_type":      task_type,
            "rule_result":    rule_result["rule_name"],
            "message":        rule_result["message"],
            "details":        rule_result.get("details", ""),
            "quality_score":  quality_data["quality_score"],
            "confidence":     quality_data["confidence"],
            "verdict":        quality_data["verdict"],
            "recommendation": quality_data["recommendation"],
        }

        status = "PASS" if final["success"] else "FAIL"
        log.info(
            f"RESULT | {status} | quality={final['quality_score']} | "
            f"confidence={final['confidence']} | {final['verdict']}"
        )

        return final

    def _unknown(self, task_type, supported):
        return {
            "success":        False,
            "task_type":      task_type,
            "rule_result":    "none",
            "message":        f"Unknown task type '{task_type}'. Supported: {supported}",
            "details":        "",
            "quality_score":  0.0,
            "confidence":     1.0,
            "verdict":        "FAILED",
            "recommendation": f"Use one of: {', '.join(supported)}"
        }
