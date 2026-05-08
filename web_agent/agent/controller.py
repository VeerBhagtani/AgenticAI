"""
WebAgent Controller — orchestrates search → fetch → evaluate loop.
"""
from logger import Logger
from searcher import search
from extractor import fetch
from evaluator import evaluate

MAX_RESULTS = 8   # max search results to try
MIN_SCORE   = 0.45


class WebAgent:
    def __init__(self, max_results: int = MAX_RESULTS):
        self.logger      = Logger()
        self.max_results = max_results

    def run(self, query: str) -> str:
        log = self.logger
        log.info(f"{'='*50}")
        log.info(f"QUERY: {query}")
        log.info(f"{'='*50}")

        # ── Step 1: Search ────────────────────────────────────
        log.step(1, f"Searching for: '{query}'")
        results = search(query, self.max_results)

        if not results:
            log.error("No search results found.")
            return "❌ No search results found. Try a different query."

        log.info(f"Found {len(results)} results.")
        for i, r in enumerate(results, 1):
            log.info(f"  [{i}] {r['title']} — {r['url']}")

        best_content  = ""
        best_score    = 0.0
        best_url      = ""
        best_title    = ""
        attempts      = 0

        # ── Step 2-6: Fetch → Evaluate loop ──────────────────
        for i, result in enumerate(results, 1):
            url   = result["url"]
            title = result["title"]

            if not url.startswith("http"):
                log.warn(f"[{i}] Skipping invalid URL: {url}")
                continue

            log.step(2, f"[{i}/{len(results)}] Fetching: {url}")
            attempts += 1

            page = fetch(url)

            if not page["success"]:
                log.warn(f"[{i}] Fetch failed — {page['error']}")
                continue

            content = page["text"]
            log.info(f"[{i}] Extracted {len(content)} chars from '{page.get('title', title)}'")

            # ── Step 5: Evaluate ──────────────────────────────
            log.step(5, f"[{i}] Evaluating content relevance...")
            eval_result = evaluate(query, content)
            score = eval_result["score"]

            log.info(
                f"[{i}] Score: {score:.3f} | Sufficient: {eval_result['sufficient']} | "
                f"{eval_result['reason']}"
            )

            if score > best_score:
                best_score   = score
                best_content = content
                best_url     = url
                best_title   = page.get("title", title)

            # ── Step 7: Stop if sufficient ────────────────────
            if eval_result["sufficient"]:
                log.info(f"✅ Sufficient answer found at result #{i} (score={score:.3f})")
                break
            else:
                log.info(f"[{i}] Not sufficient — continuing to next result...")

        # ── Final output ──────────────────────────────────────
        log.info(f"Total attempts: {attempts} | Best score: {best_score:.3f}")

        if not best_content:
            return "❌ Could not extract content from any result."

        if best_score < 0.2:
            return (
                f"⚠️  Low confidence answer (score={best_score:.2f}).\n"
                f"Source: {best_url}\n\n"
                + _summarize(best_content, 1500)
            )

        return (
            f"✅ Answer found (relevance score: {best_score:.2f})\n"
            f"Source: {best_title}\n"
            f"URL: {best_url}\n"
            f"{'─'*50}\n"
            + _summarize(best_content, 2000)
        )


def _summarize(text: str, max_chars: int) -> str:
    """Return first max_chars of content, trimmed at sentence boundary."""
    if len(text) <= max_chars:
        return text
    trimmed = text[:max_chars]
    last_period = trimmed.rfind(".")
    if last_period > max_chars // 2:
        trimmed = trimmed[:last_period + 1]
    return trimmed + "\n\n[... content truncated ...]"
