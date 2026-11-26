"""GoldenClok Contract Demo — SQLite persistence (standard library only).

This is a DEMO datastore, not the approved production schema. It stores a
synthetic wearer, one demo device, and the three record groups the sync
endpoint accepts. The production target remains Supabase PostgreSQL with the
Option D security architecture; see docs/Decisions/Phase 2 Contract Demo Scope.md.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

DISCONNECTED_AFTER_SECONDS = 3600  # CONFIRMED V1 display policy: ~1 hour

SCHEMA = """
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS wearers (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    guardian_phone  TEXT NOT NULL,
    notes           TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS devices (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    wearer_id       TEXT NOT NULL REFERENCES wearers(id),
    config_version  INTEGER NOT NULL DEFAULT 1,
    hr_high         INTEGER NOT NULL,
    hr_low          INTEGER NOT NULL,
    last_sync_at    INTEGER,
    created_at      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS device_tokens (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id   TEXT NOT NULL REFERENCES devices(id),
    token_hash  TEXT NOT NULL UNIQUE,
    created_at  INTEGER NOT NULL,
    revoked_at  INTEGER
);

CREATE TABLE IF NOT EXISTS medication_schedules (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id    TEXT NOT NULL REFERENCES devices(id),
    schedule_id  INTEGER NOT NULL,
    name         TEXT NOT NULL,
    time         TEXT NOT NULL,
    days_json    TEXT NOT NULL,
    start_date   TEXT NOT NULL,
    end_date     TEXT,
    UNIQUE (device_id, schedule_id)
);

CREATE TABLE IF NOT EXISTS health_measurements (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id    TEXT NOT NULL REFERENCES devices(id),
    record_id    TEXT NOT NULL,
    measured_at  INTEGER NOT NULL,
    heart_rate   INTEGER NOT NULL,
    received_at  INTEGER NOT NULL,
    UNIQUE (device_id, record_id)
);

CREATE TABLE IF NOT EXISTS medication_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id       TEXT NOT NULL REFERENCES devices(id),
    record_id       TEXT NOT NULL,
    schedule_id     INTEGER NOT NULL,
    scheduled_time  INTEGER NOT NULL,
    status          TEXT NOT NULL,
    received_at     INTEGER NOT NULL,
    UNIQUE (device_id, record_id)
);

CREATE TABLE IF NOT EXISTS events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id    TEXT NOT NULL REFERENCES devices(id),
    record_id    TEXT NOT NULL,
    event_type   TEXT NOT NULL,
    occurred_at  INTEGER NOT NULL,
    sms_sent     INTEGER,
    received_at  INTEGER NOT NULL,
    UNIQUE (device_id, record_id)
);

CREATE TABLE IF NOT EXISTS sync_logs (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id             TEXT NOT NULL REFERENCES devices(id),
    received_at           INTEGER NOT NULL,
    total_records         INTEGER NOT NULL,
    accepted              INTEGER NOT NULL,
    duplicates            INTEGER NOT NULL DEFAULT 0,
    rejected              INTEGER NOT NULL,
    config_version_sent   INTEGER
);

CREATE TABLE IF NOT EXISTS sync_rejections (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id     TEXT NOT NULL REFERENCES devices(id),
    record_id     TEXT,
    record_group  TEXT,
    reason        TEXT NOT NULL,
    received_at   INTEGER NOT NULL
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    # Additive migration for demo databases created before Phase 2.2.
    # CREATE TABLE IF NOT EXISTS cannot add a column to an existing table.
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(sync_logs)")}
    if "duplicates" not in columns:
        conn.execute(
            "ALTER TABLE sync_logs ADD COLUMN duplicates INTEGER NOT NULL DEFAULT 0"
        )
    conn.commit()


# --------------------------------------------------------------------------
# Lookups
# --------------------------------------------------------------------------


def device_by_token_hash(conn: sqlite3.Connection, token_hash: str) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT d.*
        FROM device_tokens t
        JOIN devices d ON d.id = t.device_id
        WHERE t.token_hash = ? AND t.revoked_at IS NULL
        """,
        (token_hash,),
    ).fetchone()
    return dict(row) if row else None


def wearer(conn: sqlite3.Connection, wearer_id: str) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM wearers WHERE id = ?", (wearer_id,)).fetchone()
    return dict(row) if row else None


def schedules(conn: sqlite3.Connection, device_id: str) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT * FROM medication_schedules
        WHERE device_id = ?
        ORDER BY schedule_id ASC
        """,
        (device_id,),
    ).fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["days"] = json.loads(item.pop("days_json"))
        items.append(item)
    return items


def first_device(conn: sqlite3.Connection) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM devices ORDER BY id ASC LIMIT 1").fetchone()
    return dict(row) if row else None


# --------------------------------------------------------------------------
# Writes
# --------------------------------------------------------------------------


def insert_record(
    conn: sqlite3.Connection, device_id: str, record: Any, now: int | None = None
) -> bool:
    """Persist one validated record.

    Returns True when a new row was written, False when the record was already
    stored. Idempotency is keyed on (device_id, record_id), as required by the
    approved data model.

    Duplicates are skipped by ``ON CONFLICT ... DO NOTHING`` rather than by
    catching every ``IntegrityError``. Any other constraint failure (foreign
    key, NOT NULL, ...) therefore propagates: a genuine database failure must
    never be acknowledged as a harmless duplicate.
    """
    now = int(now if now is not None else time.time())
    data = record.data
    if record.kind == "health_measurements":
        sql = """
            INSERT INTO health_measurements
                (device_id, record_id, measured_at, heart_rate, received_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(device_id, record_id) DO NOTHING
        """
        params = (device_id, record.record_id, data["measured_at"], data["heart_rate"], now)
    elif record.kind == "medication_records":
        sql = """
            INSERT INTO medication_records
                (device_id, record_id, schedule_id, scheduled_time, status, received_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(device_id, record_id) DO NOTHING
        """
        params = (
            device_id,
            record.record_id,
            data["schedule_id"],
            data["scheduled_time"],
            data["status"],
            now,
        )
    elif record.kind == "events":
        sms_sent = data.get("sms_sent")
        sql = """
            INSERT INTO events
                (device_id, record_id, event_type, occurred_at, sms_sent, received_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(device_id, record_id) DO NOTHING
        """
        params = (
            device_id,
            record.record_id,
            data["event_type"],
            data["occurred_at"],
            None if sms_sent is None else int(bool(sms_sent)),
            now,
        )
    else:  # pragma: no cover - guarded by contract.RECORD_KINDS
        raise ValueError(f"unsupported record kind: {record.kind}")

    cursor = conn.execute(sql, params)
    inserted = cursor.rowcount == 1
    conn.commit()
    return inserted


def log_sync(
    conn: sqlite3.Connection,
    device_id: str,
    total: int,
    accepted: int,
    rejected: int,
    config_version_sent: int | None,
    duplicates: int = 0,
    now: int | None = None,
) -> None:
    """Record one sync attempt.

    Counters are disjoint and unambiguous:
      * ``total``    - records parsed from the request
      * ``accepted`` - records newly persisted by this request
      * ``duplicates`` - records already stored under the same (device, record_id)
      * ``rejected`` - records that failed validation and were not persisted
    """
    now = int(now if now is not None else time.time())
    conn.execute(
        """
        INSERT INTO sync_logs
            (device_id, received_at, total_records, accepted, duplicates,
             rejected, config_version_sent)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (device_id, now, total, accepted, duplicates, rejected, config_version_sent),
    )
    conn.execute("UPDATE devices SET last_sync_at = ? WHERE id = ?", (now, device_id))
    conn.commit()


def log_rejection(
    conn: sqlite3.Connection,
    device_id: str,
    record_id: str | None,
    record_group: str | None,
    reason: str,
    now: int | None = None,
) -> None:
    """Store demo-safe metadata about one rejected record.

    Only identifiers, the record group and the rejection reason are kept. The
    untrusted payload itself is never stored. This is a local demo trace, not
    part of the firmware contract and not the production audit design.
    """
    now = int(now if now is not None else time.time())
    conn.execute(
        """
        INSERT INTO sync_rejections
            (device_id, record_id, record_group, reason, received_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (device_id, record_id, record_group, reason, now),
    )
    conn.commit()


# --------------------------------------------------------------------------
# Dashboard projection
# --------------------------------------------------------------------------


def dashboard_snapshot(conn: sqlite3.Connection, now: int | None = None) -> dict[str, Any]:
    now = int(now if now is not None else time.time())
    device = first_device(conn)
    if device is None:
        return {
            "demo": True,
            "seeded": False,
            "server_time": now,
            "message": "No demo device. Run from the repository root: python3 backend/seed.py",
            "rejections": [],
            "sync_logs": [],
        }

    wearer_row = wearer(conn, device["wearer_id"]) or {}
    last_sync = device.get("last_sync_at")
    connected = last_sync is not None and (now - int(last_sync)) <= DISCONNECTED_AFTER_SECONDS

    events = [
        dict(row)
        for row in conn.execute(
            """
            SELECT record_id, event_type, occurred_at, sms_sent, received_at
            FROM events WHERE device_id = ?
            ORDER BY occurred_at DESC, id DESC LIMIT 20
            """,
            (device["id"],),
        ).fetchall()
    ]
    for item in events:
        item["sms_sent"] = None if item["sms_sent"] is None else bool(item["sms_sent"])

    measurements = [
        dict(row)
        for row in conn.execute(
            """
            SELECT record_id, measured_at, heart_rate, received_at
            FROM health_measurements WHERE device_id = ?
            ORDER BY measured_at DESC, id DESC LIMIT 10
            """,
            (device["id"],),
        ).fetchall()
    ]

    medication_records = [
        dict(row)
        for row in conn.execute(
            """
            SELECT record_id, schedule_id, scheduled_time, status, received_at
            FROM medication_records WHERE device_id = ?
            ORDER BY scheduled_time DESC, id DESC LIMIT 10
            """,
            (device["id"],),
        ).fetchall()
    ]

    sync_rows = [
        dict(row)
        for row in conn.execute(
            """
            SELECT received_at, total_records, accepted, duplicates, rejected,
                   config_version_sent
            FROM sync_logs WHERE device_id = ?
            ORDER BY id DESC LIMIT 5
            """,
            (device["id"],),
        ).fetchall()
    ]

    rejections = [
        dict(row)
        for row in conn.execute(
            """
            SELECT record_id, record_group, reason, received_at
            FROM sync_rejections WHERE device_id = ?
            ORDER BY id DESC LIMIT 20
            """,
            (device["id"],),
        ).fetchall()
    ]

    return {
        "demo": True,
        "seeded": True,
        "server_time": now,
        "device": {
            "id": device["id"],
            "name": device["name"],
            "config_version": device["config_version"],
            "hr_high": device["hr_high"],
            "hr_low": device["hr_low"],
            "last_sync_at": last_sync,
            "connected": connected,
            "disconnected_after_seconds": DISCONNECTED_AFTER_SECONDS,
        },
        "wearer": {
            "id": wearer_row.get("id"),
            "name": wearer_row.get("name", ""),
            "guardian_phone": wearer_row.get("guardian_phone", ""),
            "notes": wearer_row.get("notes", ""),
        },
        "schedules": schedules(conn, device["id"]),
        "events": events,
        "measurements": measurements,
        "medication_records": medication_records,
        "sync_logs": sync_rows,
        "rejections": rejections,
    }
