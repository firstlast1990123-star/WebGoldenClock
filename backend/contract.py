"""GoldenClok Contract Demo — firmware contract helpers (standard library only).

CONFIRMED semantics implemented here
(sources: AGENTS.md section 4, project.md, docs/Roadmap.md,
docs/Architecture/Phase 1.6 section 7):

  * endpoint ``POST /api/device/sync`` with ``Authorization: Bearer <token>``
  * the device token is stored only as a SHA-256 hex digest
  * ACK is a FLAT array of record IDs, never grouped by type
  * HTTP 400 for malformed or structurally invalid JSON
  * HTTP 200 for structurally valid JSON, even when individual records fail
  * rejected records are ACKed too, so the device does not retry forever
  * ``rejected`` is optional and ignored by firmware
  * ``TAKEN`` / ``MISSED`` is decided by firmware; the Web side never overrides it
  * ``FALL`` and ``FALL_CANCELLED`` are stored as two independent records
  * ``sms_sent`` only means an AT command was issued, not that SMS was delivered
  * config payload keys and the ``config_version`` handshake

INTERIM items (NOT a firmware contract) are marked ``INTERIM`` below and are
documented in ``docs/Decisions/Phase 2 Contract Demo Scope.md``.

This module deliberately imports nothing outside the standard library so that
contract logic can be unit-tested without FastAPI installed.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

# --------------------------------------------------------------------------
# CONFIRMED contract values — do not change without joint team approval.
# --------------------------------------------------------------------------

#: Event types frozen by AGENTS.md section 4.
EVENT_TYPES = frozenset(
    {
        "FALL",
        "FALL_CANCELLED",
        "HR_HIGH",
        "HR_LOW",
        "MED_MISSED",
        "SOS",
        "LOW_BATTERY",
    }
)

#: Medication outcome vocabulary. Firmware owns the decision.
MEDICATION_STATUSES = frozenset({"TAKEN", "MISSED"})

#: Firmware schedule slot range (ESP32 hardware limit, 0-255).
SCHEDULE_ID_MIN = 0
SCHEDULE_ID_MAX = 255

#: Record groups. INTERIM NAMES — the request envelope is not yet a contract.
RECORD_KINDS = ("health_measurements", "medication_records", "events")

# --------------------------------------------------------------------------
# INTERIM choices — NOT A FIRMWARE CONTRACT.
# Each one is switchable from a single place so the real decision is cheap.
# --------------------------------------------------------------------------

#: Phase 1.6 section 7 item 7 leaves this OPEN.
#: Allowed: "omit" | "null" | "empty_object"
INTERIM_CONFIG_WHEN_UNCHANGED = "omit"

#: Top-level ``status`` value for a normal sync. Values are not contractually fixed.
INTERIM_STATUS_OK = "ok"

#: Field name carrying the device's currently known config version.
INTERIM_REQUEST_CONFIG_VERSION_KEY = "config_version"

#: Field name carrying the record groups in the request body.
INTERIM_REQUEST_RECORDS_KEY = "records"

#: Envelope rejection policies. "fail_closed_400" keeps the demo's strict
#: behaviour: the whole request is refused with HTTP 400.
#: A real firmware sending a different envelope would then be told to keep its
#: buffer and retry, which can repeat indefinitely. Do NOT connect real firmware
#: until the request schema and this rejection behaviour are agreed jointly.
INTERIM_UNKNOWN_GROUP_POLICY = "fail_closed_400"
INTERIM_INVALID_RECORD_STRUCTURE_POLICY = "fail_closed_400"
INTERIM_MISSING_RECORD_ID_POLICY = "fail_closed_400"

#: Medication schedule field conventions used by the demo seed and config.
#: The CONFIRMED contract fixes the *key names* only; these value conventions
#: are demo assumptions, NOT firmware contract text.
#: The 1=Monday..7=Sunday numbering and HH:MM format appear only in the
#: Phase 1.7.2 design, which is [PROPOSED]/[UNTESTED].
INTERIM_SCHEDULE_DAYS_CONVENTION = "1=Monday..7=Sunday"
INTERIM_SCHEDULE_TIME_FORMAT = "HH:MM (UTC+7 wall clock)"
INTERIM_SCHEDULE_END_DATE_NULLABLE = True


# --------------------------------------------------------------------------
# Errors and records
# --------------------------------------------------------------------------


class PayloadError(Exception):
    """Structural payload problem. Maps to HTTP 400 (confirmed contract)."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass
class Record:
    """One device record extracted from a structurally valid payload."""

    kind: str
    record_id: str
    data: dict[str, Any]
    accepted: bool = True
    reason: str | None = None


# --------------------------------------------------------------------------
# Token handling
# --------------------------------------------------------------------------


def sha256_hex(token: str) -> str:
    """Hash a raw device token. Only the digest is ever persisted."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# Request parsing
# --------------------------------------------------------------------------


def parse_payload(raw: bytes) -> dict[str, Any]:
    """Decode and structurally validate a sync request body.

    Raises:
        PayloadError: the body is not usable JSON or its *structure* is wrong.
            Structural failures must produce HTTP 400, never a partial ACK.
    """
    if not raw or not raw.strip():
        raise PayloadError("empty_body")

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise PayloadError("invalid_encoding") from None

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        raise PayloadError("malformed_json") from None

    if not isinstance(payload, dict):
        raise PayloadError("invalid_structure: root must be a JSON object")

    records = payload.get(INTERIM_REQUEST_RECORDS_KEY, {})
    if not isinstance(records, dict):
        raise PayloadError(
            f"invalid_structure: {INTERIM_REQUEST_RECORDS_KEY} must be an object"
        )

    for kind, items in records.items():
        if kind not in RECORD_KINDS:
            # A group this demo cannot acknowledge is refused rather than
            # silently dropped. INTERIM policy, not firmware contract text.
            if INTERIM_UNKNOWN_GROUP_POLICY == "fail_closed_400":
                raise PayloadError(f"invalid_structure: unknown record group {kind!r}")
            continue
        if not isinstance(items, list):
            if INTERIM_INVALID_RECORD_STRUCTURE_POLICY == "fail_closed_400":
                raise PayloadError(
                    f"invalid_structure: {INTERIM_REQUEST_RECORDS_KEY}.{kind} must be an array"
                )
            continue

    version = payload.get(INTERIM_REQUEST_CONFIG_VERSION_KEY)
    if version is not None and type(version) is not int:
        raise PayloadError(
            f"invalid_structure: {INTERIM_REQUEST_CONFIG_VERSION_KEY} must be an integer"
        )

    return payload


def collect_records(payload: dict[str, Any]) -> list[Record]:
    """Flatten record groups into a stable, ordered list.

    A record without a usable ``record_id`` is a structural failure: the server
    could not ACK it, which would make the device retry forever.
    """
    groups = payload.get(INTERIM_REQUEST_RECORDS_KEY, {})
    collected: list[Record] = []
    for kind in RECORD_KINDS:
        for item in groups.get(kind, []):
            if not isinstance(item, dict):
                if INTERIM_INVALID_RECORD_STRUCTURE_POLICY == "fail_closed_400":
                    raise PayloadError(
                        f"invalid_structure: {kind} entries must be JSON objects"
                    )
                continue
            record_id = item.get("record_id")
            if not isinstance(record_id, str) or not record_id.strip():
                if INTERIM_MISSING_RECORD_ID_POLICY == "fail_closed_400":
                    raise PayloadError(
                        f"invalid_structure: {kind} entry is missing record_id"
                    )
                continue
            collected.append(Record(kind=kind, record_id=record_id.strip(), data=item))
    return collected


# --------------------------------------------------------------------------
# Per-record validation (rejections, not 400s)
# --------------------------------------------------------------------------


def _int_field(data: dict[str, Any], key: str, minimum: int | None = None) -> str | None:
    value = data.get(key)
    if type(value) is not int:
        return f"{key} must be an integer"
    if minimum is not None and value < minimum:
        return f"{key} must be >= {minimum}"
    return None


def _validate_measurement(data: dict[str, Any]) -> str | None:
    for key, minimum in (("measured_at", 0), ("heart_rate", 1)):
        reason = _int_field(data, key, minimum)
        if reason:
            return reason
    return None


def _validate_medication_record(data: dict[str, Any]) -> str | None:
    reason = _int_field(data, "schedule_id", SCHEDULE_ID_MIN)
    if reason:
        return reason
    if data["schedule_id"] > SCHEDULE_ID_MAX:
        return f"schedule_id must be <= {SCHEDULE_ID_MAX}"
    reason = _int_field(data, "scheduled_time", 0)
    if reason:
        return reason
    status = data.get("status")
    if status not in MEDICATION_STATUSES:
        return f"status must be one of {sorted(MEDICATION_STATUSES)}"
    return None


def _validate_event(data: dict[str, Any]) -> str | None:
    event_type = data.get("event_type")
    if event_type not in EVENT_TYPES:
        return f"event_type must be one of {sorted(EVENT_TYPES)}"
    reason = _int_field(data, "occurred_at", 0)
    if reason:
        return reason
    if "sms_sent" in data and not isinstance(data["sms_sent"], bool):
        return "sms_sent must be a boolean when present"
    return None


_VALIDATORS = {
    "health_measurements": _validate_measurement,
    "medication_records": _validate_medication_record,
    "events": _validate_event,
}


def validate_record(record: Record) -> Record:
    """Apply per-record checks in place and return the same record."""
    reason = _VALIDATORS[record.kind](record.data)
    if reason:
        record.accepted = False
        record.reason = reason
    return record


# --------------------------------------------------------------------------
# Response construction
# --------------------------------------------------------------------------


def build_config(
    device: dict[str, Any],
    wearer: dict[str, Any] | None,
    schedules: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the CONFIRMED config block.

    Keys are frozen by project.md line 41:
    version, wearer_name, guardian_phone, hr_high, hr_low, schedule[]
    with schedule entries carrying id, name, time, days, start_date, end_date.

    Value conventions (INTERIM, not contract text): ``time`` is HH:MM UTC+7,
    ``days`` is 1=Monday..7=Sunday, ``end_date`` may be null. See the
    INTERIM_SCHEDULE_* constants above.
    """
    wearer = wearer or {}
    return {
        "version": device["config_version"],
        "wearer_name": wearer.get("name", ""),
        "guardian_phone": wearer.get("guardian_phone", ""),
        "hr_high": device["hr_high"],
        "hr_low": device["hr_low"],
        "schedule": [
            {
                "id": item["schedule_id"],
                "name": item["name"],
                "time": item["time"],
                "days": list(item["days"]),
                "start_date": item["start_date"],
                "end_date": item["end_date"],
            }
            for item in schedules
        ],
    }


def build_response(
    *,
    ack: list[str],
    rejected: list[dict[str, str]] | None = None,
    config: dict[str, Any] | None = None,
    status: str | None = None,
    server_time: int | None = None,
) -> dict[str, Any]:
    """Build a sync response.

    ``ack`` is always a flat array of record IDs. ``rejected`` is optional.
    ``config`` presence when the version is unchanged is INTERIM, not contract.
    """
    body: dict[str, Any] = {
        "status": status or INTERIM_STATUS_OK,
        "server_time": int(server_time if server_time is not None else time.time()),
        "ack": list(ack),
    }

    if rejected:
        body["rejected"] = list(rejected)

    if config is not None:
        body["config"] = config
    elif INTERIM_CONFIG_WHEN_UNCHANGED == "null":
        body["config"] = None
    elif INTERIM_CONFIG_WHEN_UNCHANGED == "empty_object":
        body["config"] = {}
    # "omit": leave the key absent entirely.

    return body


def should_send_config(device_version: int | None, server_version: int) -> bool:
    """CONFIRMED: config is sent when the server version is newer.

    A device that omits the version is treated as needing a full config.
    """
    return device_version is None or device_version < server_version
