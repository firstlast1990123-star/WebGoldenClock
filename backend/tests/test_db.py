"""Persistence tests against a temporary SQLite file. Standard library only."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import contract  # noqa: E402
import db  # noqa: E402
import seed  # noqa: E402

TOKEN = "test-token"
DEVICE_ID = "dev-1"
WEARER_ID = "wearer-1"
CANONICAL_GUARDIAN_PHONE = "+84000000000"


class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "test.db"
        self.conn = db.connect(self.path)
        db.init_schema(self.conn)
        self.conn.execute(
            "INSERT INTO wearers (id,name,guardian_phone,notes) VALUES (?,?,?,?)",
            (WEARER_ID, "Demo", "+84000000000", "synthetic"),
        )
        self.conn.execute(
            """
            INSERT INTO devices (id,name,wearer_id,config_version,hr_high,hr_low,created_at)
            VALUES (?,?,?,?,?,?,?)
            """,
            (DEVICE_ID, "Watch", WEARER_ID, 2, 120, 50, 100),
        )
        self.conn.execute(
            "INSERT INTO device_tokens (device_id, token_hash, created_at) VALUES (?,?,?)",
            (DEVICE_ID, contract.sha256_hex(TOKEN), 100),
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        self._tmp.cleanup()

    def _record(self, kind, record_id, data):
        return contract.Record(kind=kind, record_id=record_id, data=data)

    def test_token_lookup_uses_hash(self):
        found = db.device_by_token_hash(self.conn, contract.sha256_hex(TOKEN))
        self.assertIsNotNone(found)
        self.assertEqual(found["id"], DEVICE_ID)

    def test_unknown_token_returns_none(self):
        self.assertIsNone(db.device_by_token_hash(self.conn, contract.sha256_hex("nope")))

    def test_revoked_token_is_rejected(self):
        self.conn.execute("UPDATE device_tokens SET revoked_at = 1")
        self.conn.commit()
        self.assertIsNone(db.device_by_token_hash(self.conn, contract.sha256_hex(TOKEN)))

    def test_duplicate_record_id_is_idempotent(self):
        record = self._record(
            "health_measurements",
            "HR-1",
            {"measured_at": 100, "heart_rate": 70},
        )
        self.assertTrue(db.insert_record(self.conn, DEVICE_ID, record, now=100))
        self.assertFalse(db.insert_record(self.conn, DEVICE_ID, record, now=101))
        count = self.conn.execute("SELECT COUNT(*) FROM health_measurements").fetchone()[0]
        self.assertEqual(count, 1)

    def test_same_record_id_on_different_devices_is_allowed(self):
        self.conn.execute(
            """
            INSERT INTO devices (id,name,wearer_id,config_version,hr_high,hr_low,created_at)
            VALUES ('dev-2','Watch 2',?,1,120,50,100)
            """,
            (WEARER_ID,),
        )
        self.conn.commit()
        record = self._record("events", "EVT-1", {"event_type": "FALL", "occurred_at": 1})
        self.assertTrue(db.insert_record(self.conn, "dev-1", record))
        self.assertTrue(db.insert_record(self.conn, "dev-2", record))

    def test_medication_insert_writes_one_row(self):
        record = self._record(
            "medication_records",
            "MED-1",
            {"schedule_id": 1, "scheduled_time": 100, "status": "TAKEN"},
        )
        self.assertTrue(db.insert_record(self.conn, DEVICE_ID, record, now=100))
        count = self.conn.execute("SELECT COUNT(*) FROM medication_records").fetchone()[0]
        self.assertEqual(count, 1)

    def test_duplicate_insert_reports_no_new_row(self):
        record = self._record("events", "EVT-1", {"event_type": "SOS", "occurred_at": 1})
        self.assertTrue(db.insert_record(self.conn, DEVICE_ID, record, now=100))
        self.assertFalse(db.insert_record(self.conn, DEVICE_ID, record, now=101))
        count = self.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        self.assertEqual(count, 1)

    def test_unrelated_integrity_failure_propagates(self):
        # Foreign-key violation is not a duplicate-key conflict and must never
        # be silently ACKed.
        record = self._record("events", "EVT-X", {"event_type": "SOS", "occurred_at": 1})
        with self.assertRaises(sqlite3.IntegrityError):
            db.insert_record(self.conn, "does-not-exist", record)
        self.conn.rollback()
        count = self.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        self.assertEqual(count, 0)

    def test_sync_log_updates_last_sync(self):
        db.log_sync(self.conn, DEVICE_ID, total=3, accepted=2, rejected=1,
                    config_version_sent=2, now=500)
        device = db.first_device(self.conn)
        self.assertEqual(device["last_sync_at"], 500)

    def test_sync_log_counters_are_disjoint(self):
        db.log_sync(
            self.conn,
            DEVICE_ID,
            total=10,
            accepted=4,
            duplicates=3,
            rejected=2,
            config_version_sent=1,
            now=700,
        )
        row = self.conn.execute(
            "SELECT total_records, accepted, duplicates, rejected FROM sync_logs"
        ).fetchone()
        self.assertEqual(tuple(row), (10, 4, 3, 2))
        snapshot = db.dashboard_snapshot(self.conn, now=700)
        self.assertEqual(snapshot["sync_logs"][0]["duplicates"], 3)

    def test_rejection_trace_stores_metadata_only(self):
        db.log_rejection(
            self.conn,
            DEVICE_ID,
            "MED-9",
            "medication_records",
            "status must be one of ['MISSED', 'TAKEN']",
            now=800,
        )
        row = self.conn.execute(
            "SELECT record_id, record_group, reason, received_at FROM sync_rejections"
        ).fetchone()
        self.assertEqual(row["record_id"], "MED-9")
        self.assertEqual(row["record_group"], "medication_records")
        self.assertEqual(row["received_at"], 800)
        # The trace has no column capable of holding an untrusted payload.
        columns = {
            item["name"] for item in self.conn.execute("PRAGMA table_info(sync_rejections)")
        }
        self.assertEqual(
            columns,
            {"id", "device_id", "record_id", "record_group", "reason", "received_at"},
        )

    def test_dashboard_reports_disconnected_after_one_hour(self):
        db.log_sync(self.conn, DEVICE_ID, 0, 0, 0, None, now=1000)
        fresh = db.dashboard_snapshot(self.conn, now=1000 + 3599)
        self.assertTrue(fresh["device"]["connected"])
        stale = db.dashboard_snapshot(self.conn, now=1000 + 3601)
        self.assertFalse(stale["device"]["connected"])

    def test_dashboard_shape(self):
        snapshot = db.dashboard_snapshot(self.conn, now=1000)
        self.assertTrue(snapshot["demo"])
        self.assertTrue(snapshot["seeded"])
        for key in ("device", "wearer", "schedules", "events", "measurements",
                    "medication_records", "sync_logs"):
            self.assertIn(key, snapshot)


class SeedConvergenceTests(unittest.TestCase):
    """A normal re-seed must repair the frozen synthetic wearer fixture."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "demo.db"

    def tearDown(self):
        self._tmp.cleanup()

    def test_normal_reseed_restores_canonical_wearer_fixture(self):
        seed.seed(self.path, reset=False)

        # Simulate drift, e.g. a hand-edited or stale demo row.
        conn = db.connect(self.path)
        try:
            conn.execute(
                "UPDATE wearers SET guardian_phone = ? WHERE id = ?",
                ("+849999999999", seed.WEARER_ID),
            )
            conn.commit()
            current = conn.execute(
                "SELECT guardian_phone FROM wearers WHERE id = ?", (seed.WEARER_ID,)
            ).fetchone()
            self.assertEqual(current["guardian_phone"], "+849999999999")
        finally:
            conn.close()

        # Normal seed without --reset.
        seed.seed(self.path, reset=False)

        conn = db.connect(self.path)
        try:
            wearer = conn.execute(
                "SELECT name, guardian_phone, notes FROM wearers WHERE id = ?",
                (seed.WEARER_ID,),
            ).fetchone()
            self.assertEqual(wearer["guardian_phone"], CANONICAL_GUARDIAN_PHONE)
            self.assertEqual(wearer["name"], "Demo Wearer (SIMULATED)")
            self.assertIn("Synthetic demo profile", wearer["notes"])

            counts = {
                table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in (
                    "wearers",
                    "devices",
                    "device_tokens",
                    "medication_schedules",
                    "events",
                )
            }
            self.assertEqual(
                counts,
                {
                    "wearers": 1,
                    "devices": 1,
                    "device_tokens": 1,
                    "medication_schedules": 3,
                    "events": 1,
                },
            )
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
