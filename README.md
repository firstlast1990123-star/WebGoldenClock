# WebGoldenClock

Smart wearable and companion platform for elderly care — **Web platform**.

> **This repository currently contains a reduced Contract Demo, not the production
> platform.** Option D (Hybrid Architecture) was approved as the **target**
> production architecture in Phase 1.7.2: Supabase PostgreSQL + Supabase Auth +
> React SPA + FastAPI sync ingestion. Production implementation has **not
> started** and remains subject to security readiness, unresolved decisions and
> separate implementation authorization. See
> `docs/Architecture/Phase 1.7.2 - Hybrid Security Architecture Review.md` and
> `docs/Decisions/Phase 2 Contract Demo Scope.md`.

## What is in this repository

| Path | Purpose |
| :-- | :-- |
| `backend/` | FastAPI Contract Demo (sync endpoint + demo dashboard) |
| `backend/contract.py` | Confirmed contract rules plus the named `INTERIM_*` demo assumptions (stdlib only, unit-tested) |
| `backend/db.py` | SQLite persistence (stdlib only) |
| `backend/app.py` | FastAPI application |
| `backend/seed.py` | Synthetic demo data generator |
| `backend/examples/sync-request.json` | Example sync payload (**interim shape**) |
| `backend/tests/` | Contract, persistence and HTTP integration tests (stdlib `unittest`) |
| `docs/` | Architecture, decisions, roadmap, task board |
| `project.md` | Official progress log |

## Environment prerequisites

- Python **3.12**.
- The demo server needs **FastAPI** and **Uvicorn** (`backend/requirements.txt`
  lists the versions).
- The seed script and the contract/persistence tests use only the Python
  standard library.

**Current state of this development machine (checked 2026-11-25):** the system
Python 3.12 interpreter is PEP 668 `EXTERNALLY-MANAGED` and does **not** have
FastAPI or Uvicorn. A local, git-ignored `.venv/` exists with **FastAPI
0.165.0** and **Uvicorn 0.54.0**; use `.venv/bin/python` for the server and the
HTTP integration tests. `pytest` is not installed.

No package was installed and no `sudo` command was run while producing this
demo. Do **not** work around this with `--break-system-packages`; on a fresh
clone, provision a proper virtual environment.

The HTTP layer has been exercised locally: manual smoke tests and the automated
HTTP integration tests in `backend/tests/test_http_contract.py` run against a
temporary SQLite database and do not touch `backend/demo.db`.

## Run the demo

All commands below run **from the repository root**.

Terminal 1:

```bash
# 1. Seed synthetic demo data (safe to re-run; --reset starts over)
python3 backend/seed.py --reset

# 2. Start the server on localhost only
.venv/bin/python -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8000
```

Dashboard URL: **http://127.0.0.1:8000/**

`--app-dir backend` lets `app:app` import the flat `contract` / `db` modules
while every command still runs from the repository root. Stop the server
before running `seed.py --reset` again: `--reset` removes the demo database
and its `-wal` / `-shm` / `-journal` sidecars.

The dashboard is unauthenticated by design and is intended for local
demonstration only. Do not bind it to a public interface.

Health check (from the repository root):

```bash
curl -s http://127.0.0.1:8000/health
```

## Simulate a device sync

Keep Uvicorn running and use a **second terminal**, again from the repository
root. The seed script prints the demo token. It is a fixed demo string, **not a
credential**.

> **The request envelope below is an INTERIM demo assumption, not a finalized
> firmware integration contract.** The assumptions are recorded as I-1…I-12 in
> `docs/Decisions/Phase 2 Contract Demo Scope.md`. Do **not** connect real
> firmware until the Firmware team and the Web team agree the unresolved
> contract items: a real device sending a different envelope would receive
> `HTTP 400` and could retry indefinitely. The local Contract Demo is **not
> production-ready**.

```bash
curl -s -X POST http://127.0.0.1:8000/api/device/sync \
  -H "Authorization: Bearer demo-device-token-do-not-use-in-production" \
  -H "Content-Type: application/json" \
  --data @backend/examples/sync-request.json
```

Expected response (only `server_time` varies; the ACK is a **flat** array of
every record ID, and the config block lists all three seeded schedules):

```json
{
  "status": "ok",
  "server_time": 1795446291,
  "ack": [
    "DEMO-HR-0001",
    "DEMO-MED-0001",
    "DEMO-EVT-0002",
    "DEMO-EVT-0003"
  ],
  "config": {
    "version": 3,
    "wearer_name": "Demo Wearer (SIMULATED)",
    "guardian_phone": "+84000000000",
    "hr_high": 120,
    "hr_low": 50,
    "schedule": [
      {
        "id": 0,
        "name": "Demo Morning Pill (SIMULATED)",
        "time": "08:00",
        "days": [1, 2, 3, 4, 5],
        "start_date": "2026-11-01",
        "end_date": null
      },
      {
        "id": 1,
        "name": "Demo Evening Pill (SIMULATED)",
        "time": "20:30",
        "days": [1, 2, 3, 4, 5, 6, 7],
        "start_date": "2026-11-01",
        "end_date": "2026-12-31"
      },
      {
        "id": 2,
        "name": "Demo Weekend Pill (SIMULATED)",
        "time": "10:15",
        "days": [6, 7],
        "start_date": "2026-11-01",
        "end_date": null
      }
    ]
  }
}
```

Replaying the same payload returns `200` with the same ACK and writes **no
duplicate measurement / medication / event rows** — idempotency is keyed on
`(device_id, record_id)`. A replay does still add a new `sync_logs` row (with
its `duplicates` counter) and refresh `last_sync_at`; those are sync attempts,
not records.

### Contract failure cases

```bash
# Malformed JSON -> HTTP 400 (device keeps its buffer)
curl -s -o /dev/null -w '%{http_code}\n' -X POST \
  http://127.0.0.1:8000/api/device/sync \
  -H "Authorization: Bearer demo-device-token-do-not-use-in-production" \
  --data '{"records": '

# Missing token -> HTTP 401
curl -s -o /dev/null -w '%{http_code}\n' -X POST \
  http://127.0.0.1:8000/api/device/sync --data '{}'
```

A payload with structurally valid JSON but a bad record (for example an
undocumented `event_type`) returns **HTTP 200**, stores the valid records,
rejects the bad one, and still ACKs every record ID so the device does not
retry forever. Rejections are recorded in `sync_rejections` as demo-safe
metadata only: device ID, record ID, record group, reason and timestamp — never
the raw payload.

## Tests

```bash
python3 -m unittest discover -s backend/tests -v
```

The suite contains **41 contract/persistence tests** plus **6 HTTP integration
tests** (47 total). The HTTP tests spawn the existing `.venv/bin/python -m
uvicorn` against a freshly seeded temporary database and use standard-library
`urllib`; they skip cleanly if that interpreter or Uvicorn is unavailable. They
never touch `backend/demo.db`.

The contract/persistence tests cover payload parsing and structural errors,
flat ACK ordering, rejection-while-ACKing, medication status/event-type
validation, config key set, config-version handshake, SHA-256 token hashing,
idempotency (first insert, duplicate, same ID on another device), propagation
of unrelated integrity failures, distinct `accepted` / `duplicates` /
`rejected` sync counters, rejection-trace metadata, token revocation and the
disconnect-after-one-hour rule.

The HTTP integration tests additionally cover `GET /health`,
`GET /api/dashboard`, valid sync, replay idempotency and duplicate counters,
401 authentication failures, 400 structural failures, mixed valid/invalid
records with ACK + rejection metadata, the config-version handshake and
dashboard state after a mixed sync. `openapi.json` is disabled, so the only
HTTP surface is `/health`, `/api/dashboard` and `/api/device/sync`.

## Contract rules honoured (and rules not guessed)

Implemented from confirmed sources: flat ACK array, HTTP 400/200, per-record
rejection with ACK, Bearer device token hashed with SHA-256, firmware-owned
`TAKEN`/`MISSED`, independent `FALL`/`FALL_CANCELLED` records, `sms_sent`
meaning, config key set and `config_version` handshake.

**Deliberately not guessed** (still `OPEN`): bootstrap token provisioning,
hardware `device_id` format, response shape when the config version is
unchanged, `FALL`/`FALL_CANCELLED` notification policy, exact `unpaired` JSON.
The request body shape used by the demo is an **interim assumption** and is
labelled as such in `docs/Decisions/Phase 2 Contract Demo Scope.md`. Real
firmware must not be connected until the Firmware team and the Web team agree
the unresolved items and the INTERIM assumptions are explicitly replaced.

## Security notes

- Local-only: bind to `127.0.0.1`.
- Synthetic data only; no real personal or health data.
- The only token in this repository is a fixed demo string, not a credential.
- Local SQLite files, virtual environments and `.env*` files are git-ignored.
- No production security is claimed. RLS, guardian authentication and role
  separation exist only as approved architecture, not as code.
