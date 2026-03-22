# Copyright 2024 LGPD Sentinel AI Contributors
# Licensed under the Apache License, Version 2.0

"""
SQLite database layer for audit history.
Uses the standard library sqlite3 — zero extra dependencies.
"""

import json
import logging
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generator

logger = logging.getLogger(__name__)


def _resolve_db_path() -> Path:
    """Resolve DB path: env var > config > fallback to project-relative."""
    env = os.environ.get("LGPD_DB_PATH")
    if env:
        return Path(env)
    try:
        from src.core.config import settings
        if settings.DB_PATH:
            return Path(settings.DB_PATH)
    except Exception:
        pass
    return Path(__file__).parent.parent.parent / "data" / "sentinel.db"


DB_PATH = _resolve_db_path()


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

            CREATE TABLE IF NOT EXISTS api_keys (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key                 TEXT NOT NULL UNIQUE,
                plan                    TEXT NOT NULL DEFAULT 'free',
                email                   TEXT,
                stripe_customer_id      TEXT,
                stripe_subscription_id  TEXT,
                active                  INTEGER NOT NULL DEFAULT 1,
                trial_ends_at           TEXT,
                created_at              TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            );

            CREATE TABLE IF NOT EXISTS usage_monthly (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key     TEXT NOT NULL,
                month       TEXT NOT NULL,
                mappings    INTEGER NOT NULL DEFAULT 0,
                dpias       INTEGER NOT NULL DEFAULT 0,
                dsrs        INTEGER NOT NULL DEFAULT 0,
                UNIQUE(api_key, month)
            );
        """)
    # Migration: add trial_ends_at to existing installs that predate this column
    with sqlite3.connect(db_path) as conn:
        try:
            conn.execute("ALTER TABLE api_keys ADD COLUMN trial_ends_at TEXT")
            logger.info("Migrated api_keys: added trial_ends_at column")
        except sqlite3.OperationalError:
            pass  # column already exists
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


# ─── API Keys & Plans ─────────────────────────────────────────────────────────


def create_api_key(email: str | None = None, db_path: Path = DB_PATH) -> str:
    """Generate and persist a new free-tier API key with a 7-day Pro trial. Returns the key string."""
    key = "lgpd_" + secrets.token_urlsafe(32)
    trial_ends_at = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with get_conn(db_path) as conn:
        conn.execute(
            "INSERT INTO api_keys (api_key, plan, email, trial_ends_at) VALUES (?, 'free', ?, ?)",
            (key, email, trial_ends_at),
        )
    return key


def is_trial_active(api_key: str, db_path: Path = DB_PATH) -> bool:
    """Return True if the key has an active 7-day Pro trial."""
    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT trial_ends_at FROM api_keys WHERE api_key = ? AND active = 1",
            (api_key,),
        ).fetchone()
    if not row or not row["trial_ends_at"]:
        return False
    trial_end = datetime.strptime(row["trial_ends_at"], "%Y-%m-%dT%H:%M:%SZ")
    return datetime.utcnow() < trial_end


def get_api_key(api_key: str, db_path: Path = DB_PATH) -> dict[str, Any] | None:
    """Return API key record or None if not found / inactive."""
    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM api_keys WHERE api_key = ? AND active = 1", (api_key,)
        ).fetchone()
        return dict(row) if row else None


def update_api_key_plan(
    api_key: str,
    plan: str,
    stripe_customer_id: str | None = None,
    stripe_subscription_id: str | None = None,
    db_path: Path = DB_PATH,
) -> None:
    """Upgrade or downgrade an API key's plan."""
    with get_conn(db_path) as conn:
        conn.execute(
            """
            UPDATE api_keys
            SET plan = ?, stripe_customer_id = ?, stripe_subscription_id = ?
            WHERE api_key = ?
            """,
            (plan, stripe_customer_id, stripe_subscription_id, api_key),
        )


# ─── Usage tracking ───────────────────────────────────────────────────────────


def _current_month() -> str:
    return datetime.utcnow().strftime("%Y-%m")


def increment_usage(api_key: str, endpoint: str, db_path: Path = DB_PATH) -> None:
    """Increment usage counter for the current month. endpoint: 'mappings'|'dpias'|'dsrs'."""
    month = _current_month()
    allowed = {"mappings", "dpias", "dsrs"}
    if endpoint not in allowed:
        return
    with get_conn(db_path) as conn:
        conn.execute(
            f"""
            INSERT INTO usage_monthly (api_key, month, {endpoint})
            VALUES (?, ?, 1)
            ON CONFLICT(api_key, month) DO UPDATE SET {endpoint} = {endpoint} + 1
            """,
            (api_key, month),
        )


def get_usage(api_key: str, db_path: Path = DB_PATH) -> dict[str, int]:
    """Return current month usage for an API key."""
    month = _current_month()
    with get_conn(db_path) as conn:
        row = conn.execute(
            "SELECT mappings, dpias, dsrs FROM usage_monthly WHERE api_key = ? AND month = ?",
            (api_key, month),
        ).fetchone()
        if row:
            return dict(row)
        return {"mappings": 0, "dpias": 0, "dsrs": 0}
