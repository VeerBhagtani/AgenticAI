"""
DecisionEngine — main orchestrator.
classify(goal) → suggest plan → return full Decision object.
"""
from classifier import classify
from planner import suggest_plan
from logger import Logger

class DecisionEngine:
    def __init__(self):
        self.logger = Logger()

    def decide(self, goal: str) -> dict:
        log = self.logger
        log.info(f"{'='*55}")
        log.info(f"GOAL: {goal}")

        # ── Classify ──────────────────────────────────────────
        clf = classify(goal)
        log.info(
            f"CLASSIFICATION: {clf['category']} "
            f"| confidence={clf['confidence']:.2f} "
            f"| web_score={clf['web_score']} pc_score={clf['pc_score']}"
        )
        log.info(f"REASONING: {clf['reasoning']}")

        # ── Plan ──────────────────────────────────────────────
        plan = suggest_plan(goal, clf["category"])
        log.info(f"SUGGESTED AGENT: {plan['agent']}")
        for step in plan["steps"]:
            log.info(f"  {step}")

        # ── Assemble Decision ─────────────────────────────────
        decision = {
            "goal":           goal,
            "category":       clf["category"],
            "agent":          clf["agent"],
            "confidence":     clf["confidence"],
            "web_score":      clf["web_score"],
            "pc_score":       clf["pc_score"],
            "reasoning":      clf["reasoning"],
            "suggested_steps":plan["steps"],
            "suggested_params":plan["params"],
        }

        log.info(f"DECISION: {clf['category']} (confidence={clf['confidence']:.2f})")
        return decision
