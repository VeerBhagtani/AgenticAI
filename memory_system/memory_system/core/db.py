"""
Storage layer — SQLite via stdlib only.

Tables:
  tasks        — one row per task execution
  task_steps   — one row per step within a task
  tags         — keyword tags per task (for retrieval)
"""
import sqlite3, os, json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "db", "memory.db")

DDL = """
CREATE TABLE IF NOT EXISTS tasks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    goal          TEXT    NOT NULL,
    category      TEXT,                        -- WEB_AGENT | PC_AGENT | BOTH
    command       TEXT,                        -- raw user input
    success       INTEGER NOT NULL DEFAULT 0,  -- 1=success 0=fail
    quality_score REAL    DEFAULT 0.0,
    retries       INTEGER DEFAULT 0,
    duration_sec  REAL    DEFAULT 0.0,
    output        TEXT,
    error         TEXT,
    metadata      TEXT,                        -- JSON blob for extras
    created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS task_steps (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id    INTEGER NOT NULL REFERENCES tasks(id),
    step_name  TEXT,
    action     TEXT,
    success    INTEGER DEFAULT 0,
    output     TEXT,
    error      TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tags (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL REFERENCES tasks(id),
    tag     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_success    ON tasks(success);
CREATE INDEX IF NOT EXISTS idx_tasks_category   ON tasks(category);
CREATE INDEX IF NOT EXISTS idx_tags_tag         ON tags(tag);
"""

def get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(DDL)
    conn.commit()
    return conn
