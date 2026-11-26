#!/usr/bin/env python3
"""Create or reset the local Contract Demo database with SIMULATED data.

Usage (from the repository root):
    python3 backend/seed.py                 # seed backend/demo.db (idempotent)
    python3 backend/seed.py --reset         # delete and recreate the demo DB
    python3 backend/seed.py --db /tmp/demo.db

``--reset`` removes only the configured database file and its SQLite sidecars
(-wal, -shm, -journal). Stop any running Uvicorn process first: deleting a
database that a live server still has open is unsafe.

The device token printed below is a fixed DEMO string. It is not a credential
and must never be used anywhere real.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import contract  # noqa: E402
import db  # noqa: E402

DEMO_TOKEN = "demo-device-token-do-not-use-in-production"
DEVICE_ID = "demo-device-001"
WEARER_ID = "demo-wearer-001"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = Path(__file__).resolve().parent / "demo.db"

#: SQLite creates these next to the database while WAL mode is active.
SIDECAR_SUFFIXES = ("-wal", "-shm", "-journal")


def database_files(path: Path) -> list[Path]:
    """The configured database file and only its known SQLite sidecars."""
    return [path] + [path.with_name(path.name + suffix) for suffix in SIDECAR_SUFFIXES]


def reset_database(path: Path) -> None:
    """Remove the demo database and its sidecars.

    Refuses any path that is not a ``.db`` file so a mistyped ``--db`` argument
    cannot delete something unrelated. Only the configured path and its
    sidecars are touched.
    """
    if path.suffix != ".db":
        raise SystemExit(
            f"refusing to reset {path}: the demo database file must end with '.db'"
        )
    if path.exists() and not path.is_file():
        raise SystemExit(f"refusing to reset {path}: not a regular file")
    for target in database_files(path):
        try:
            target.unlink()
        except FileNotFoundError:
            continue


def seed(path: Path, reset: bool) -> None:
    if reset:
        reset_database(path)
    conn = db.connect(path)
    try:
        db.init_schema(conn)
        now = int(time.time())

        # UPSERT so a plain re-seed converges the frozen synthetic fixture even
        # if the row was edited by hand. The other inserts stay INSERT OR IGNORE.
        conn.execute(
            """
            INSERT INTO wearers (id, name, guardian_phone, notes)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                guardian_phone = excluded.guardian_phone,
                notes = excluded.notes
            """,
            (
                WEARER_ID,
                "Demo Wearer (SIMULATED)",
                "+84000000000",
                "Synthetic demo profile. Not a real person. No real health data.",
            ),
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO devices
                (id, name, wearer_id, config_version, hr_high, hr_low, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (DEVICE_ID, "Demo Watch (SIMULATED)", WEARER_ID, 3, 120, 50, now),
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO device_tokens (device_id, token_hash, created_at)
            VALUES (?, ?, ?)
            """,
            (DEVICE_ID, contract.sha256_hex(DEMO_TOKEN), now),
        )

        schedules = [
            (0, "Demo Morning Pill (SIMULATED)", "08:00", [1, 2, 3, 4, 5], "2026-11-01", None),
            (1, "Demo Evening Pill (SIMULATED)", "20:30", [1, 2, 3, 4, 5, 6, 7], "2026-11-01", "2026-12-31"),
            (2, "Demo Weekend Pill (SIMULATED)", "10:15", [6, 7], "2026-11-01", None),
        ]
        for schedule_id, name, clock, days, start_date, end_date in schedules:
            conn.execute(
                """
                INSERT OR IGNORE INTO medication_schedules
                    (device_id, schedule_id, name, time, days_json, start_date, end_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (DEVICE_ID, schedule_id, name, clock, json.dumps(days), start_date, end_date),
            )

        # One synthetic event so the dashboard is not empty before the first sync.
        conn.execute(
            """
            INSERT OR IGNORE INTO events
                (device_id, record_id, event_type, occurred_at, sms_sent, received_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (DEVICE_ID, "DEMO-EVT-0001", "LOW_BATTERY", now - 7200, None, now - 7200),
        )
        conn.commit()
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the GoldenClok Contract Demo database.")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite file path")
    parser.add_argument("--reset", action="store_true", help="delete and recreate the database")
    args = parser.parse_args()

    path = Path(args.db).expanduser()
    seed(path, args.reset)

    print("GoldenClok Contract Demo — SIMULATED data only")
    print(f"Database : {path}")
    print(f"Device   : {DEVICE_ID}")
    print(f"Token    : {DEMO_TOKEN}  (DEMO ONLY, not a credential)")
    print()
    print(f"Next steps. Run both commands from the repository root: {REPO_ROOT}")
    print()
    print("  # 1. start the server (localhost only)")
    print("  python3 -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8000")
    print("  # 2. open the dashboard")
    print("  http://127.0.0.1:8000/")
    print()
    print("  # 3. in a SECOND terminal, also from the repository root, send a sync")
    print(
        "  curl -s -X POST http://127.0.0.1:8000/api/device/sync "
        f'-H "Authorization: Bearer {DEMO_TOKEN}" '
        '-H "Content-Type: application/json" '
        "--data @backend/examples/sync-request.json"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
