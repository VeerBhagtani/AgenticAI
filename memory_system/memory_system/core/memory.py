"""
MemoryStore — CRUD + retrieval for tasks, steps, and tags.
"""
import json, re
from datetime import datetime
from core.db import get_conn


# ── Write ─────────────────────────────────────────────────────

def save_task(
    goal:          str,
    command:       str       = "",
    category:      str       = "",
    success:       bool      = False,
    quality_score: float     = 0.0,
    retries:       int       = 0,
    duration_sec:  float     = 0.0,
    output:        str       = "",
    error:         str       = "",
    metadata:      dict      = None,
    steps:         list      = None,   # list of step dicts
    tags:          list      = None,   # list of strings
) -> int:
    """Persist a completed task. Returns task_id."""
    conn = get_conn()
    now  = datetime.utcnow().isoformat()

    # Auto-generate tags from goal if none provided
    if tags is None:
        tags = _extract_tags(goal + " " + command)

    cur = conn.execute(
        """INSERT INTO tasks
           (goal, category, command, success, quality_score, retries,
            duration_sec, output, error, metadata, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            goal, category, command,
            1 if success else 0,
            quality_score, retries, duration_sec,
            output[:2000] if output else "",
            error[:1000]  if error  else "",
            json.dumps(metadata or {}),
            now
        )
    )
    task_id = cur.lastrowid

    # Steps
    for s in (steps or []):
        conn.execute(
            """INSERT INTO task_steps
               (task_id, step_name, action, success, output, error, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (
                task_id,
                s.get("name", ""),
                s.get("action", ""),
                1 if s.get("success") else 0,
                s.get("output", "")[:1000],
                s.get("error", "")[:500],
                now
            )
        )

    # Tags
    for tag in set(tags):
        if tag:
            conn.execute("INSERT INTO tags (task_id, tag) VALUES (?,?)", (task_id, tag))

    conn.commit()
    conn.close()
    return task_id


# ── Read ──────────────────────────────────────────────────────

def get_task(task_id: int) -> dict | None:
    conn = get_conn()
    row  = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    if not row:
        conn.close()
        return None
    result = _row_to_dict(row)
    result["steps"] = _get_steps(conn, task_id)
    result["tags"]  = _get_tags(conn, task_id)
    conn.close()
    return result


def get_recent(limit: int = 10, success_only: bool = False) -> list[dict]:
    conn  = get_conn()
    where = "WHERE success=1" if success_only else ""
    rows  = conn.execute(
        f"SELECT * FROM tasks {where} ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    results = [_row_to_dict(r) for r in rows]
    conn.close()
    return results


def find_similar(query: str, limit: int = 5) -> list[dict]:
    """
    Retrieve past tasks similar to query.
    Strategy:
      1. Tag match  (fast, exact keyword overlap)
      2. Goal LIKE  (substring match on goal text)
    Results ranked by: tag_matches DESC, success DESC, id DESC
    """
    conn   = get_conn()
    q_tags = _extract_tags(query)

    # Tag match
    matched_ids = {}
    for tag in q_tags:
        rows = conn.execute(
            "SELECT task_id FROM tags WHERE tag=?", (tag,)
        ).fetchall()
        for r in rows:
            matched_ids[r["task_id"]] = matched_ids.get(r["task_id"], 0) + 1

    # Sort by match count
    ranked_ids = sorted(matched_ids.items(), key=lambda x: x[1], reverse=True)

    # Supplement with LIKE matches if not enough
    if len(ranked_ids) < limit:
        words = q_tags[:3]
        for word in words:
            rows = conn.execute(
                "SELECT id FROM tasks WHERE goal LIKE ? ORDER BY id DESC LIMIT 10",
                (f"%{word}%",)
            ).fetchall()
            for r in rows:
                if r["id"] not in matched_ids:
                    ranked_ids.append((r["id"], 0))

    results = []
    seen = set()
    for task_id, match_count in ranked_ids[:limit]:
        if task_id in seen:
            continue
        seen.add(task_id)
        task = get_task(task_id)
        if task:
            task["_match_score"] = match_count
            results.append(task)

    conn.close()
    return results


def get_stats() -> dict:
    conn = get_conn()
    row  = conn.execute("""
        SELECT
            COUNT(*)                              AS total,
            SUM(success)                          AS passed,
            COUNT(*) - SUM(success)               AS failed,
            ROUND(AVG(quality_score), 2)          AS avg_quality,
            ROUND(AVG(retries), 2)                AS avg_retries,
            ROUND(AVG(duration_sec), 2)           AS avg_duration
        FROM tasks
    """).fetchone()
    by_cat = conn.execute("""
        SELECT category, COUNT(*) as count, SUM(success) as passed
        FROM tasks GROUP BY category
    """).fetchall()
    conn.close()
    return {
        **dict(row),
        "by_category": [dict(r) for r in by_cat]
    }


def delete_task(task_id: int) -> bool:
    conn = get_conn()
    conn.execute("DELETE FROM task_steps WHERE task_id=?", (task_id,))
    conn.execute("DELETE FROM tags       WHERE task_id=?", (task_id,))
    cur = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    return cur.rowcount > 0


# ── Helpers ───────────────────────────────────────────────────

STOP_WORDS = {
    "a","an","the","is","in","on","at","to","of","and","or","for",
    "with","that","this","it","be","as","do","get","if","by","from"
}

def _extract_tags(text: str) -> list[str]:
    words = re.findall(r"\b[a-z]{3,}\b", text.lower())
    return list({w for w in words if w not in STOP_WORDS})

def _row_to_dict(row) -> dict:
    d = dict(row)
    d["success"] = bool(d.get("success"))
    try:
        d["metadata"] = json.loads(d.get("metadata") or "{}")
    except Exception:
        d["metadata"] = {}
    return d

def _get_steps(conn, task_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM task_steps WHERE task_id=? ORDER BY id", (task_id,)
    ).fetchall()
    return [dict(r) for r in rows]

def _get_tags(conn, task_id: int) -> list[str]:
    rows = conn.execute("SELECT tag FROM tags WHERE task_id=?", (task_id,)).fetchall()
    return [r["tag"] for r in rows]
