import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .config import db_path


def _connect() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mode TEXT NOT NULL,
                    target_role TEXT NOT NULL DEFAULT '',
                    input_text TEXT NOT NULL,
                    profile_text TEXT NOT NULL DEFAULT '',
                    result_json TEXT NOT NULL,
                    processing_mode TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
    finally:
        conn.close()


def _row_to_dict(row: sqlite3.Row, full: bool = True) -> Dict[str, Any]:
    result = json.loads(row["result_json"])
    data: Dict[str, Any] = {
        "id": row["id"],
        "mode": row["mode"],
        "target_role": row["target_role"],
        "processing_mode": row["processing_mode"],
        "created_at": row["created_at"],
        "summary": (result.get("profile_summary") or "")[:140],
    }
    if full:
        data.update(
            input_text=row["input_text"],
            profile_text=row["profile_text"],
            result=result,
        )
    return data


def insert_record(mode: str, target_role: str, input_text: str, profile_text: str,
                  result: Dict[str, Any], processing_mode: str) -> Dict[str, Any]:
    created = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conn = _connect()
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO profiles (mode, target_role, input_text, profile_text, result_json,"
                " processing_mode, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (mode, target_role, input_text, profile_text, json.dumps(result), processing_mode, created),
            )
            new_id = cur.lastrowid
    finally:
        conn.close()
    return {"id": new_id, "created_at": created}


def list_records() -> List[Dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM profiles ORDER BY id DESC LIMIT 100").fetchall()
    finally:
        conn.close()
    return [_row_to_dict(r, full=False) for r in rows]


def get_record(record_id: int) -> Optional[Dict[str, Any]]:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM profiles WHERE id = ?", (record_id,)).fetchone()
    finally:
        conn.close()
    return _row_to_dict(row) if row else None


def delete_record(record_id: int) -> bool:
    conn = _connect()
    try:
        with conn:
            cur = conn.execute("DELETE FROM profiles WHERE id = ?", (record_id,))
            return cur.rowcount > 0
    finally:
        conn.close()
