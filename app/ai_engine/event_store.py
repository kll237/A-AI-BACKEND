"""SQLite-backed event store for AI-engine alerts.

Each processor already persists an alert as a frame jpg plus a JSON metadata
file. This module additionally records every alert in a local SQLite database
(``app.core.config.settings.SQLITE_DB_PATH``) so events can be queried,
filtered and replayed without scanning the filesystem.

All writes are best-effort: a storage failure is logged and swallowed so it can
never interrupt a detection pipeline.
"""
import json
import logging
import sqlite3
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,
    camera_id   TEXT,
    event_type  TEXT    NOT NULL,
    rule_id     TEXT,
    label       TEXT,
    confidence  REAL,
    frame_path  TEXT,
    payload     TEXT
)
"""

_lock = threading.Lock()
_conn: Optional[sqlite3.Connection] = None


def _get_conn() -> sqlite3.Connection:
    """Lazily open (and keep open) the shared SQLite connection. Importing
    settings lazily avoids any module-import cycle with app.core.config."""
    global _conn
    if _conn is None:
        from app.core.config import settings

        path = settings.SQLITE_DB_PATH
        if path is None:
            raise RuntimeError("SQLITE_DB_PATH is not configured")
        path.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(path), check_same_thread=False)
        _conn.execute(_SCHEMA)
        _conn.commit()
    return _conn


def add_event(
    event_type: str,
    camera_id: Optional[str] = None,
    rule_id: Optional[str] = None,
    label: Optional[str] = None,
    confidence: Optional[float] = None,
    frame_path: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    """Persist a single alert event. Never raises into the caller."""
    try:
        ts = datetime.now().isoformat(timespec="seconds")
        payload_json = json.dumps(payload, ensure_ascii=False) if payload else None
        with _lock:
            conn = _get_conn()
            conn.execute(
                "INSERT INTO events "
                "(timestamp, camera_id, event_type, rule_id, label, confidence, frame_path, payload) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ts, camera_id, event_type, rule_id, label, confidence, frame_path, payload_json),
            )
            conn.commit()
    except Exception as e:  # storage is best-effort
        logger.warning(f"Failed to persist event to SQLite: {e}")


def recent_events(limit: int = 100, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return the most recent events (newest first), optionally filtered by type.
    Used for replay / dashboard queries."""
    try:
        with _lock:
            conn = _get_conn()
            if event_type:
                rows = conn.execute(
                    "SELECT id, timestamp, camera_id, event_type, rule_id, label, "
                    "confidence, frame_path, payload FROM events "
                    "WHERE event_type = ? ORDER BY id DESC LIMIT ?",
                    (event_type, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, timestamp, camera_id, event_type, rule_id, label, "
                    "confidence, frame_path, payload FROM events "
                    "ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        cols = ["id", "timestamp", "camera_id", "event_type", "rule_id",
                "label", "confidence", "frame_path", "payload"]
        out = []
        for r in rows:
            d = dict(zip(cols, r))
            if d.get("payload"):
                try:
                    d["payload"] = json.loads(d["payload"])
                except Exception:
                    pass
            out.append(d)
        return out
    except Exception as e:
        logger.warning(f"Failed to read events from SQLite: {e}")
        return []
