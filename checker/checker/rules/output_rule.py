"""
Rule: OUTPUT
Checks if expected text/output is present in a file or string.
Supports: exact match, partial match, regex.
"""
import os
import re

def check(params: dict) -> dict:
    expected = params.get("expected", "").strip()
    source   = params.get("source", "").strip()

    if not expected:
        return _fail("No expected text provided.", 0.0)
    if not source:
        return _fail("No source provided.", 0.0)

    # Load content — file or raw string
    if os.path.isfile(source):
        try:
            with open(source, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            source_label = f"file:{source}"
        except Exception as e:
            return _fail(f"Cannot read file '{source}': {e}", 0.0)
    else:
        content = source
        source_label = "string"

    if not content.strip():
        return _fail("Source is empty.", 0.0)

    # ── Match strategies ──────────────────────────────────────
    exact_match   = expected.lower() in content.lower()
    words         = expected.lower().split()
    matched_words = [w for w in words if w in content.lower()]
    word_ratio    = len(matched_words) / max(len(words), 1)

    # Try regex (gracefully)
    regex_match = False
    try:
        regex_match = bool(re.search(expected, content, re.IGNORECASE))
    except re.error:
        pass

    # ── Quality scoring ───────────────────────────────────────
    if exact_match:
        quality = 1.0
        match_type = "exact"
    elif regex_match:
        quality = 0.85
        match_type = "regex"
    elif word_ratio >= 0.8:
        quality = 0.75
        match_type = f"partial ({len(matched_words)}/{len(words)} words)"
    elif word_ratio >= 0.5:
        quality = 0.5
        match_type = f"partial ({len(matched_words)}/{len(words)} words)"
    else:
        quality = word_ratio * 0.4
        match_type = f"weak ({len(matched_words)}/{len(words)} words)"

    success = quality >= 0.5

    return {
        "success":   success,
        "rule_name": "output_present",
        "quality":   round(quality, 3),
        "message":   f"Match: {match_type} in {source_label}",
        "details":   f"Matched words: {matched_words}"
    }

def _fail(msg, quality):
    return {"success": False, "rule_name": "output_present",
            "quality": quality, "message": msg, "details": ""}
