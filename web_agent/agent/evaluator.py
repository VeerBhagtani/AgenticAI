"""
Evaluator — scores how well page content answers the query.
Pure local logic, no API needed.
"""
import re
from collections import Counter

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]{3,}\b", text.lower())

# Common stop words to ignore
STOP = {
    "the","and","for","are","but","not","you","all","can","her","was","one",
    "our","out","day","get","has","him","his","how","its","let","man","new",
    "now","old","see","two","way","who","boy","did","its","she","too","use"
}

def _keywords(text: str) -> set[str]:
    return {w for w in _tokenize(text) if w not in STOP}

def evaluate(query: str, content: str) -> dict:
    """
    Returns:
        {
          "score": float (0.0 - 1.0),
          "sufficient": bool,
          "matched_keywords": list,
          "reason": str
        }
    """
    if not content or len(content) < 100:
        return {"score": 0.0, "sufficient": False, "matched_keywords": [], "reason": "Content too short"}

    query_kws  = _keywords(query)
    content_kws = _keywords(content)

    if not query_kws:
        return {"score": 0.5, "sufficient": True, "matched_keywords": [], "reason": "No keywords to evaluate"}

    matched = query_kws & content_kws
    base_score = len(matched) / len(query_kws)

    # Bonus: keyword density (how often they appear)
    content_tokens = _tokenize(content)
    token_freq = Counter(content_tokens)
    density_bonus = min(0.2, sum(token_freq[k] for k in matched) / max(len(content_tokens), 1))

    # Bonus: content length (longer = more likely thorough)
    length_bonus = min(0.1, len(content) / 50000)

    score = min(1.0, base_score + density_bonus + length_bonus)
    sufficient = score >= 0.45 and len(content) >= 300

    reason = (
        f"{len(matched)}/{len(query_kws)} keywords matched "
        f"({', '.join(list(matched)[:5])}{'...' if len(matched) > 5 else ''})"
    )

    return {
        "score":            round(score, 3),
        "sufficient":       sufficient,
        "matched_keywords": list(matched),
        "reason":           reason
    }
