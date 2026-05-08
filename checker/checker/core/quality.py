"""
Quality Engine
Takes a rule result and computes:
  - quality_score  : how good/useful the result is (0.0 - 1.0)
  - confidence     : how certain we are about the verdict (0.0 - 1.0)
"""

# Weight of each rule's raw quality score
RULE_WEIGHTS = {
    "file_exists":   1.0,
    "app_running":   0.9,
    "output_present":1.0,
    "cmd_output":    0.95,
}

def assess(rule_result: dict, task_type: str) -> dict:
    """
    Returns enriched dict with:
      quality_score, confidence, verdict, recommendation
    """
    success  = rule_result.get("success", False)
    raw_q    = rule_result.get("quality", 0.0)
    rule_name = rule_result.get("rule_name", task_type)

    weight = RULE_WEIGHTS.get(rule_name, 1.0)

    # ── Quality Score ─────────────────────────────────────────
    quality_score = round(raw_q * weight, 3)

    # ── Confidence ────────────────────────────────────────────
    # High confidence when: success=True + high quality, OR success=False + quality=0
    # Low confidence when: borderline quality
    if success:
        if quality_score >= 0.8:   confidence = 0.95
        elif quality_score >= 0.6: confidence = 0.80
        elif quality_score >= 0.4: confidence = 0.65
        else:                      confidence = 0.50
    else:
        if quality_score == 0.0:   confidence = 0.95  # definitely failed
        elif quality_score < 0.2:  confidence = 0.85
        elif quality_score < 0.4:  confidence = 0.70
        else:                      confidence = 0.55  # borderline

    # ── Verdict ───────────────────────────────────────────────
    if success and quality_score >= 0.8:
        verdict = "HIGH QUALITY"
    elif success and quality_score >= 0.5:
        verdict = "ACCEPTABLE"
    elif success and quality_score < 0.5:
        verdict = "LOW QUALITY — task done but result is poor"
    elif not success and quality_score > 0.3:
        verdict = "PARTIAL — task incomplete"
    else:
        verdict = "FAILED"

    # ── Recommendation ────────────────────────────────────────
    rec = _recommend(success, quality_score, rule_name)

    return {
        "quality_score":  quality_score,
        "confidence":     round(confidence, 3),
        "verdict":        verdict,
        "recommendation": rec
    }

def _recommend(success: bool, quality: float, rule: str) -> str:
    if success and quality >= 0.8:
        return "Task completed successfully. No action needed."
    if success and quality >= 0.5:
        return "Task done. Consider verifying the result manually."
    if success and quality < 0.5:
        return "Task technically done but output quality is low. Review and redo if needed."
    if not success and quality > 0.2:
        return "Partial completion detected. Check for errors and retry."
    return "Task failed. Retry or investigate the cause."
