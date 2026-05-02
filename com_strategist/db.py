"""
SQLite persistence for strategy audit history.
"""

import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.getenv("HISTORY_DB_PATH", "/app/data/strategy_history.db")


def _conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS strategy_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT    NOT NULL,
                file         TEXT    NOT NULL,
                news_used    TEXT    NOT NULL DEFAULT '[]',
                improvements INTEGER NOT NULL DEFAULT 0,
                status       TEXT    NOT NULL DEFAULT 'done',
                created_at   TEXT    NOT NULL
            )
        """)


def insert_record(name: str, file: str, news_used: list, improvements: int) -> dict:
    created_at = datetime.utcnow().isoformat()
    with _conn() as c:
        cur = c.execute(
            """INSERT INTO strategy_history
               (name, file, news_used, improvements, status, created_at)
               VALUES (?, ?, ?, ?, 'done', ?)""",
            (name, file, json.dumps(news_used, ensure_ascii=False), improvements, created_at),
        )
        row_id = cur.lastrowid
    return _get_one(row_id)


def _get_one(record_id: int) -> dict | None:
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM strategy_history WHERE id = ?", (record_id,)
        ).fetchone()
    return _to_dict(row) if row else None


def get_all() -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM strategy_history ORDER BY id DESC"
        ).fetchall()
    return [_to_dict(r) for r in rows]


def _to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["news_used"] = json.loads(d["news_used"])
    try:
        dt = datetime.fromisoformat(d["created_at"])
        d["date"] = dt.strftime("%b %d, %Y")
    except Exception:
        d["date"] = d["created_at"]
    return d
