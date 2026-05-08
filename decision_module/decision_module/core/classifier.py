"""
Classifier — scores a goal against WEB_AGENT and PC_AGENT keyword sets,
then returns a Decision with confidence and reasoning.

Categories:
  WEB_AGENT   → needs information from the internet
  PC_AGENT    → needs a local system action
  BOTH        → needs info first, then act
  UNKNOWN     → cannot determine
"""

import re

# ── Keyword signal tables ─────────────────────────────────────
# Each entry: (pattern, weight)

WEB_SIGNALS = [
    # Strong info-seeking verbs
    (r"\b(search|find|look up|lookup|google|research|browse|fetch)\b",    2.0),
    (r"\b(what is|what are|who is|who are|how does|why does|when did)\b", 2.0),
    (r"\b(latest|current|recent|news|update|today|now)\b",                1.5),
    # Information nouns
    (r"\b(information|info|data|facts|answer|result|article|website)\b",  1.5),
    (r"\b(price|weather|stock|score|definition|meaning|explain)\b",       1.5),
    (r"\b(how to|tutorial|guide|learn|understand)\b",                     1.2),
    # Web-specific
    (r"\b(url|link|page|site|online|internet|web)\b",                     1.0),
]

PC_SIGNALS = [
    # Strong action verbs
    (r"\b(open|launch|start|run|execute|close|kill|stop)\b",              2.0),
    (r"\b(create|make|write|save|delete|remove|rename|move|copy)\b",      2.0),
    (r"\b(install|uninstall|download|upload|send|print)\b",               1.8),
    # File/system nouns
    (r"\b(file|folder|directory|app|application|program|process)\b",      1.5),
    (r"\b(command|cmd|terminal|script|task|schedule)\b",                  1.5),
    # System-specific
    (r"\b(notepad|excel|word|chrome|firefox|browser|calculator)\b",       2.0),
    (r"\b(desktop|windows|registry|settings|control panel)\b",            1.5),
    (r"\b(shutdown|restart|sleep|log off|reboot)\b",                      2.0),
]

# Composite patterns → force BOTH
BOTH_SIGNALS = [
    r"\b(find .+ (and|then) (open|create|save|run))\b",
    r"\b(search .+ (and|then) (open|run|install))\b",
    r"\b(look up .+ (and|then))\b",
    r"\b(get .+ (price|info|data) .+ (and|then|to))\b",
]


def _score(text: str, signals: list) -> float:
    total = 0.0
    text  = text.lower()
    for pattern, weight in signals:
        if re.search(pattern, text, re.IGNORECASE):
            total += weight
    return round(total, 2)

def _force_both(text: str) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in BOTH_SIGNALS)


def classify(goal: str) -> dict:
    """
    Returns:
    {
      "category":   "WEB_AGENT" | "PC_AGENT" | "BOTH" | "UNKNOWN",
      "confidence": float (0.0–1.0),
      "web_score":  float,
      "pc_score":   float,
      "reasoning":  str,
      "agent":      str  (human-readable agent name)
    }
    """
    web_score = _score(goal, WEB_SIGNALS)
    pc_score  = _score(goal, PC_SIGNALS)
    total     = web_score + pc_score

    # Force BOTH check
    if _force_both(goal):
        return _result("BOTH", web_score, pc_score,
                       confidence=0.85,
                       reason="Goal explicitly chains an info-lookup with a system action.")

    if total == 0:
        return _result("UNKNOWN", 0, 0,
                       confidence=0.0,
                       reason="No recognisable intent signals found.")

    # Confidence = how dominant the winning side is
    if web_score > 0 and pc_score > 0:
        ratio = max(web_score, pc_score) / total
        if ratio < 0.65:                      # nearly tied → BOTH
            return _result("BOTH", web_score, pc_score,
                           confidence=round(ratio, 2),
                           reason=f"Mixed signals: web={web_score} pc={pc_score}.")

    if web_score >= pc_score:
        conf = min(1.0, web_score / (web_score + 1))
        return _result("WEB_AGENT", web_score, pc_score,
                       confidence=round(conf, 2),
                       reason=f"Info-seeking signals dominate (web={web_score} vs pc={pc_score}).")
    else:
        conf = min(1.0, pc_score / (pc_score + 1))
        return _result("PC_AGENT", web_score, pc_score,
                       confidence=round(conf, 2),
                       reason=f"Action signals dominate (pc={pc_score} vs web={web_score}).")


AGENT_LABELS = {
    "WEB_AGENT": "Web Agent  🌐  (search + extract information)",
    "PC_AGENT":  "PC Agent   💻  (execute local system action)",
    "BOTH":      "Both Agents 🔗  (fetch info → then act)",
    "UNKNOWN":   "Unknown    ❓  (cannot determine — needs clarification)",
}

def _result(category, web, pc, confidence, reason):
    return {
        "category":   category,
        "agent":      AGENT_LABELS[category],
        "confidence": confidence,
        "web_score":  web,
        "pc_score":   pc,
        "reasoning":  reason,
    }
