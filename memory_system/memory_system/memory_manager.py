"""
MemoryManager — the public API other modules (pc_agent, web_agent, loop_controller) use.

Usage:
    from memory_manager import MemoryManager
    mm = MemoryManager()

    # Record a task
    task_id = mm.record(goal="open notepad", command="open notepad",
                        category="PC_AGENT", success=True, ...)

    # Find similar past tasks
    similar = mm.recall("open application")

    # Stats
    mm.stats()
"""
import time
from core.memory import save_task, get_task, get_recent, find_similar, get_stats, delete_task
from core.logger import Logger


class MemoryManager:
    def __init__(self):
        self.logger = Logger()
        self._timers = {}  # goal → start_time

    # ── Recording ─────────────────────────────────────────────

    def start_task(self, goal: str):
        """Call before executing a task to start the timer."""
        self._timers[goal] = time.time()
        self.logger.info(f"TASK STARTED: {goal}")

    def record(
        self,
        goal:          str,
        command:       str   = "",
        category:      str   = "",
        success:       bool  = False,
        quality_score: float = 0.0,
        retries:       int   = 0,
        output:        str   = "",
        error:         str   = "",
        steps:         list  = None,
        tags:          list  = None,
        metadata:      dict  = None,
    ) -> int:
        """Persist a completed task. Returns task_id."""
        duration = 0.0
        if goal in self._timers:
            duration = round(time.time() - self._timers.pop(goal), 3)

        task_id = save_task(
            goal=goal, command=command, category=category,
            success=success, quality_score=quality_score,
            retries=retries, duration_sec=duration,
            output=output, error=error,
            steps=steps, tags=tags, metadata=metadata,
        )

        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.logger.info(
            f"TASK RECORDED [{task_id}] {status} | "
            f"category={category} quality={quality_score:.2f} "
            f"retries={retries} duration={duration}s"
        )
        return task_id

    # ── Retrieval ─────────────────────────────────────────────

    def recall(self, query: str, limit: int = 5) -> list[dict]:
        """Find past tasks similar to query."""
        self.logger.info(f"RECALL: '{query}'")
        results = find_similar(query, limit)
        self.logger.info(f"  Found {len(results)} similar task(s)")
        for r in results:
            status = "✅" if r["success"] else "❌"
            self.logger.info(f"  [{r['id']}] {status} score={r.get('_match_score',0)} | {r['goal']}")
        return results

    def recent(self, limit: int = 10, success_only: bool = False) -> list[dict]:
        """Get N most recent tasks."""
        return get_recent(limit, success_only)

    def get(self, task_id: int) -> dict | None:
        """Fetch a single task by ID."""
        return get_task(task_id)

    def stats(self) -> dict:
        """Return aggregate stats."""
        s = get_stats()
        self.logger.info(
            f"STATS: total={s['total']} passed={s['passed']} failed={s['failed']} "
            f"avg_quality={s['avg_quality']} avg_retries={s['avg_retries']}"
        )
        return s

    def delete(self, task_id: int) -> bool:
        ok = delete_task(task_id)
        if ok:
            self.logger.info(f"DELETED task {task_id}")
        return ok
