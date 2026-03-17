# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
SQLite database layer for audit history.
Uses the standard library sqlite3 — zero extra dependencies.
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "data" / "sentinel.db"


def init_db(db_path: Path = DB_PATH) -> None:
    """Create tables if they don't exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS mapping_audits (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                company     TEXT,
                context     TEXT,
                items_json  TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            );

            CREATE TABLE IF NOT EXISTS dpia_audits (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                company             TEXT,
                treatment           TEXT,
                risk_level          TEXT,
                compliance_score    REAL,
                result_json         TEXT NOT NULL,
                created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            );
        """)
    logger.info("Database initialized at %s", db_path)


@contextmanager
def get_conn(db_path: Path = DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """Context manager yielding a sqlite3 connection with row_factory set."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ─── Mapping audits ───────────────────────────────────────────────────────────

def save_mapping_audit(
    company: str,
    context: str | None,
    items: list[dict[str, Any]],
    result: dict[str, Any],
    db_path: Path = DB_PATH,
) -> int:
    """Persist a data-mapping audit and return its ID."""
    with get_conn(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO mapping_audits (company, context, items_json, result_json)
            VALUES (?, ?, ?, ?)
            """,
            (company, context, json.dumps(items), json.dumps(result)),
        )
        return cur.lastrowid


def list_mapping_audits(limit: int = 50, db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    """Return the most recent mapping audits."""
    with get_conn(db_path) as conn:
        rows = conn.execute(
            "SELECT id, company, context, created_at FROM mapping_audits ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_mapping_audit(audit_id: int, db_path: Path = DB_PATH) -> dict[str, Any] | None:
    """Return a single mapping audit by ID (full JSON included)."""
    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM mapping_audits WHERE id = ?", (audit_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["items"]  = json.loads(d.pop("items_json"))
        d["result"] = json.loads(d.pop("result_json"))
        return d


# ─── DPIA audits ──────────────────────────────────────────────────────────────

def save_dpia_audit(
    company: str,
    treatment: str,
    risk_level: str,
    compliance_score: float,
    result: dict[str, Any],
    db_path: Path = DB_PATH,
) -> int:
    """Persist a DPIA audit and return its ID."""
    with get_conn(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO dpia_audits
                (company, treatment, risk_level, compliance_score, result_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (company, treatment, risk_level, compliance_score, json.dumps(result)),
        )
        return cur.lastrowid


def list_dpia_audits(limit: int = 50, db_path: Path = DB_PATH) -> list[dict[str, Any]]:
    """Return the most recent DPIA audits."""
    with get_conn(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, company, treatment, risk_level, compliance_score, created_at
            FROM dpia_audits ORDER BY id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_dpia_audit(audit_id: int, db_path: Path = DB_PATH) -> dict[str, Any] | None:
    """Return a single DPIA audit by ID (full JSON included)."""
    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM dpia_audits WHERE id = ?", (audit_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["result"] = json.loads(d.pop("result_json"))
        return d
