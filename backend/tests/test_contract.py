"""Contract-layer tests. Standard library only: runnable without FastAPI.

Run:
    python3 -m unittest discover -s backend/tests -v
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import contract  # noqa: E402


def payload(**overrides):
    base = {
        "config_version": 0,
        "records": {
            "health_measurements": [
                {"record_id": "HR-1", "measured_at": 1795000000, "heart_rate": 78}
            ],
            "medication_records": [
                {
                    "record_id": "MED-1",
                    "schedule_id": 0,
                    "scheduled_time": 1794979200,
                    "status": "TAKEN",
                }
            ],
            "events": [
                {
                    "record_id": "EVT-1",
                    "event_type": "FALL",
                    "occurred_at": 1794990000,
                    "sms_sent": True,
                }
            ],
        },
    }
    base.update(overrides)
    return base


class ParsePayloadTests(unittest.TestCase):
    def test_valid_payload_round_trips(self):
        data = payload()
        parsed = contract.parse_payload(json.dumps(data).encode())
        self.assertEqual(parsed["config_version"], 0)
        self.assertIn("events", parsed["records"])

    def test_empty_body_is_structural_error(self):
        with self.assertRaises(contract.PayloadError) as ctx:
            contract.parse_payload(b"")
        self.assertEqual(ctx.exception.reason, "empty_body")

    def test_malformed_json_is_structural_error(self):
        with self.assertRaises(contract.PayloadError) as ctx:
            contract.parse_payload(b'{"records": ')
        self.assertEqual(ctx.exception.reason, "malformed_json")

    def test_non_object_root_is_structural_error(self):
        with self.assertRaises(contract.PayloadError):
            contract.parse_payload(b"[]")

    def test_records_must_be_object(self):
        with self.assertRaises(contract.PayloadError):
            contract.parse_payload(json.dumps({"records": []}).encode())

    def test_unknown_record_group_is_structural_error(self):
        body = json.dumps({"records": {"unknown_group": []}}).encode()
        with self.assertRaises(contract.PayloadError) as ctx:
            contract.parse_payload(body)
        self.assertIn("unknown record group", ctx.exception.reason)

    def test_non_integer_config_version_is_structural_error(self):
        with self.assertRaises(contract.PayloadError):
            contract.parse_payload(json.dumps({"config_version": "3"}).encode())

    def test_record_without_id_is_structural_error(self):
        body = json.dumps(
            {"records": {"events": [{"event_type": "FALL", "occurred_at": 1}]}}
        ).encode()
        parsed = contract.parse_payload(body)
        with self.assertRaises(contract.PayloadError) as ctx:
            contract.collect_records(parsed)
        self.assertIn("record_id", ctx.exception.reason)

    def test_non_object_record_entry_is_structural_error(self):
        body = json.dumps({"records": {"events": ["not-an-object"]}}).encode()
        parsed = contract.parse_payload(body)
        with self.assertRaises(contract.PayloadError) as ctx:
            contract.collect_records(parsed)
        self.assertIn("JSON objects", ctx.exception.reason)


class AcknowledgeTests(unittest.TestCase):
    def test_ack_is_flat_array_of_ids_in_stable_order(self):
        parsed = contract.parse_payload(json.dumps(payload()).encode())
        records = contract.collect_records(parsed)
        body = contract.build_response(ack=[r.record_id for r in records], server_time=123)
        self.assertEqual(body["ack"], ["HR-1", "MED-1", "EVT-1"])
        self.assertIsInstance(body["ack"], list)
        self.assertEqual(body["server_time"], 123)

    def test_rejected_records_are_still_acknowledged(self):
        parsed = contract.parse_payload(json.dumps(payload()).encode())
        records = contract.collect_records(parsed)
        # Force a rejection on the medication record only.
        records[1].data["status"] = "LOST"
        contract.validate_record(records[1])
        self.assertFalse(records[1].accepted)

        body = contract.build_response(
            ack=[r.record_id for r in records],
            rejected=[{"record_id": "MED-1", "reason": records[1].reason}],
        )
        self.assertIn("MED-1", body["ack"])
        self.assertEqual(len(body["ack"]), 3)
        self.assertEqual(body["rejected"][0]["record_id"], "MED-1")

    def test_rejected_key_absent_when_nothing_rejected(self):
        body = contract.build_response(ack=["A"])
        self.assertNotIn("rejected", body)


class ValidationTests(unittest.TestCase):
    def _validate(self, kind, data):
        record = contract.Record(kind=kind, record_id="X", data=data)
        return contract.validate_record(record)

    def test_medication_status_must_be_firmware_vocabulary(self):
        record = self._validate(
            "medication_records",
            {"schedule_id": 1, "scheduled_time": 1, "status": "SKIPPED"},
        )
        self.assertFalse(record.accepted)
        self.assertIn("status", record.reason)

    def test_medication_schedule_id_range(self):
        record = self._validate(
            "medication_records",
            {"schedule_id": 256, "scheduled_time": 1, "status": "TAKEN"},
        )
        self.assertFalse(record.accepted)

    def test_undocumented_event_type_is_rejected_not_stored(self):
        record = self._validate(
            "events", {"event_type": "EARTHQUAKE", "occurred_at": 1}
        )
        self.assertFalse(record.accepted)

    def test_all_confirmed_event_types_pass(self):
        for event_type in sorted(contract.EVENT_TYPES):
            with self.subTest(event_type=event_type):
                record = self._validate(
                    "events", {"event_type": event_type, "occurred_at": 1}
                )
                self.assertTrue(record.accepted)

    def test_sms_sent_must_be_boolean(self):
        record = self._validate(
            "events", {"event_type": "SOS", "occurred_at": 1, "sms_sent": "yes"}
        )
        self.assertFalse(record.accepted)

    def test_heart_rate_must_be_positive_integer(self):
        record = self._validate(
            "health_measurements", {"measured_at": 1, "heart_rate": 0}
        )
        self.assertFalse(record.accepted)


class ConfigTests(unittest.TestCase):
    DEVICE = {"config_version": 3, "hr_high": 120, "hr_low": 50}
    WEARER = {"name": "Demo Wearer", "guardian_phone": "+84000000000"}
    SCHEDULES = [
        {
            "schedule_id": 0,
            "name": "Morning",
            "time": "08:00",
            "days": [1, 2, 3],
            "start_date": "2026-11-01",
            "end_date": None,
        }
    ]

    def test_config_payload_keys_are_the_confirmed_set(self):
        config = contract.build_config(self.DEVICE, self.WEARER, self.SCHEDULES)
        self.assertEqual(
            set(config),
            {"version", "wearer_name", "guardian_phone", "hr_high", "hr_low", "schedule"},
        )
        self.assertEqual(
            set(config["schedule"][0]),
            {"id", "name", "time", "days", "start_date", "end_date"},
        )

    def test_config_omitted_when_version_unchanged(self):
        # INTERIM behaviour, explicitly switchable in contract.py.
        self.assertEqual(contract.INTERIM_CONFIG_WHEN_UNCHANGED, "omit")
        self.assertFalse(contract.should_send_config(3, 3))
        body = contract.build_response(ack=[], config=None)
        self.assertNotIn("config", body)

    def test_config_sent_when_server_is_newer(self):
        self.assertTrue(contract.should_send_config(2, 3))

    def test_device_without_version_gets_full_config(self):
        self.assertTrue(contract.should_send_config(None, 3))

    def test_end_date_null_passes_through(self):
        # INTERIM: end_date nullability is not confirmed firmware contract text.
        config = contract.build_config(self.DEVICE, self.WEARER, self.SCHEDULES)
        self.assertIsNone(config["schedule"][0]["end_date"])
        self.assertTrue(contract.INTERIM_SCHEDULE_END_DATE_NULLABLE)


class InterimPolicyTests(unittest.TestCase):
    """Locks the documented demo policy constants (not firmware contract text)."""

    def test_request_envelope_policies_are_fail_closed(self):
        self.assertEqual(contract.INTERIM_UNKNOWN_GROUP_POLICY, "fail_closed_400")
        self.assertEqual(
            contract.INTERIM_INVALID_RECORD_STRUCTURE_POLICY, "fail_closed_400"
        )
        self.assertEqual(contract.INTERIM_MISSING_RECORD_ID_POLICY, "fail_closed_400")

    def test_schedule_value_conventions_are_documented_as_interim(self):
        self.assertEqual(contract.INTERIM_SCHEDULE_DAYS_CONVENTION, "1=Monday..7=Sunday")
        self.assertEqual(
            contract.INTERIM_SCHEDULE_TIME_FORMAT, "HH:MM (UTC+7 wall clock)"
        )


class TokenTests(unittest.TestCase):
    def test_sha256_hex_known_vector(self):
        self.assertEqual(
            contract.sha256_hex("abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )

    def test_hash_is_deterministic_and_not_the_token(self):
        token = "demo-device-token-do-not-use-in-production"
        self.assertEqual(contract.sha256_hex(token), contract.sha256_hex(token))
        self.assertNotIn(token, contract.sha256_hex(token))


if __name__ == "__main__":
    unittest.main()
