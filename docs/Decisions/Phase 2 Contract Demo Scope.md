---
type: decision-record
project: GoldenClok
phase: Phase 2 — Contract Demo (reduced scope)
date: 2026-11-23
status: AUTHORIZED — DEMO ONLY, NOT PRODUCTION ARCHITECTURE
---

# Phase 2 — Contract Demo Scope (Reduced)

## 1. Authorization and rationale

- **2026-11-23 — Project Owner** authorized implementation of the Web platform in parallel with submission documentation.
- **Lead Architect** selected a **reduced Contract Demo** scope because:
  - the repository contained **zero application code** before this task;
  - the submission deadline is **2026-11-26**;
  - the approved production architecture (Option D, `Phase 1.7.2`) still has unresolved implementation blockers and remains `[UNTESTED]`.

**This record authorizes the demo only.** It does **not** approve the production stack, does **not** promote `PROVISIONAL` choices to `CONFIRMED`, and does **not** close any `OPEN` protocol decision.

## 2. Frozen stack (this task only)

| Layer | Choice |
| :-- | :-- |
| Language | Python 3.12 |
| HTTP framework | FastAPI |
| Server | Uvicorn |
| Persistence | SQLite via the standard library `sqlite3` |
| Frontend | Static HTML + CSS + vanilla JavaScript served by FastAPI |
| Network | Local only, bound to `127.0.0.1` |

**Explicitly excluded:** React, Vite, Node.js, Supabase, SQLAlchemy, Alembic, Docker, cloud deployment.

## 3. What the contract demo implements

- `GET /health`
- `POST /api/device/sync` with `Authorization: Bearer <device_token>`
- device token verification against a stored **SHA-256 hex digest** (raw token never persisted)
- flat ACK array of record IDs
- `HTTP 400` for malformed or structurally invalid JSON
- `HTTP 200` for structurally valid JSON, including per-record rejections
- rejected records are ACKed as well (prevents endless device retry)
- each rejection is recorded in `sync_rejections` as demo-safe metadata only:
  device ID, record ID, record group, reason, timestamp (never the raw payload)
- idempotency keyed on `(device_id, record_id)` via `ON CONFLICT ... DO NOTHING`
- `sync_logs` keeps disjoint counters: `total_records`, `accepted` (newly
  persisted), `duplicates` (already stored), `rejected` (failed validation)
- `TAKEN` / `MISSED` accepted from firmware and never overridden
- `FALL` and `FALL_CANCELLED` stored as two independent records
- `sms_sent` presented as "AT command issued", never as delivery confirmation
- `config` block emitted with the confirmed key set when `server.config_version` is newer
- read-only `GET /api/dashboard` for the demo UI (**not** a firmware contract)
- disconnect status after ~1 hour without sync, with the threshold shown in the UI
- dashboard timestamps rendered in `Asia/Ho_Chi_Minh` (UTC+7)
- `docs_url`, `redoc_url` and `openapi_url` all disabled

## 4. Confirmed contract elements honoured

Sources: `AGENTS.md` §4, `project.md` lines 38–58, `docs/Roadmap.md` (Contract guardrails), `docs/Architecture/Phase 1.6` §7.

| Element | Status |
| :-- | :-- |
| Endpoint `POST /api/device/sync` | CONFIRMED — implemented |
| Bearer device token, SHA-256 at rest | CONFIRMED — implemented |
| ACK = flat array of record IDs | CONFIRMED — implemented |
| HTTP 400 / 200 semantics | CONFIRMED — implemented |
| `rejected` optional field | CONFIRMED — implemented |
| Event type vocabulary | CONFIRMED — implemented |
| `FALL` / `FALL_CANCELLED` stored separately | CONFIRMED — implemented |
| `sms_sent` meaning | CONFIRMED — implemented |
| Config payload key set | CONFIRMED — implemented |
| Disconnect after ~1 hour without sync | CONFIRMED V1 display policy (`project.md`) — implemented |
| Sync cadence and `unpaired` device behaviour | CONFIRMED — **not implemented** (device-side behaviour, out of demo scope) |
| Retention windows (7 / 30 days) | CONFIRMED — **not implemented** (server-side retention job, out of demo scope) |

## 5. INTERIM assumptions — NOT A FIRMWARE CONTRACT

These were required to make a runnable demo. Where practical each choice is isolated in a named `INTERIM_*` constant in `backend/contract.py`; all must be replaced by a joint decision, never silently promoted.

This section is a warning list, **not** a firmware integration contract. The request envelope and record shapes below are demo assumptions; they must not be read as protocol agreed with the Firmware team.

| # | Item | Demo choice | Why it is interim |
| :-- | :-- | :-- | :-- |
| I-1 | **Sync request body schema** | `{"config_version": <int>, "records": {"health_measurements": [...], "medication_records": [...], "events": [...]}}` | The request schema is **not documented anywhere** in the repository. Only the response envelope, ACK and HTTP semantics are confirmed. |
| I-2 | **Response when config version is unchanged** | `config` key **omitted** | `OPEN` per `Phase 1.6` §7 item 7. Switchable via `INTERIM_CONFIG_WHEN_UNCHANGED` (`omit` / `null` / `empty_object`). |
| I-3 | **Top-level `status` value** | `"ok"` | Response fields `status`, `server_time`, `ack`, `config` are confirmed to exist; the value vocabulary is not. |
| I-4 | **Record `record_id` format** | opaque string | Device-generated; format is `OPEN`. |
| I-5 | **Unauthenticated/invalid token status code** | `401` | Standard HTTP; the contract only fixes 400/200, so 401 does not conflict, but it is not contract text. |
| I-6 | **Dashboard read endpoint** | `GET /api/dashboard` | Demo UI convenience, not part of the firmware contract. |
| I-7 | **Unknown record group policy** | fail closed: whole request → `HTTP 400` (`INTERIM_UNKNOWN_GROUP_POLICY = "fail_closed_400"`) | The request envelope is not documented. Refusing is safer than ACKing data this demo cannot persist, but a differing real envelope will be refused. |
| I-8 | **Invalid record structure policy** | fail closed: `records` not an object, group not an array, or entry not an object → `HTTP 400` (`INTERIM_INVALID_RECORD_STRUCTURE_POLICY = "fail_closed_400"`) | Not contract text; the contract only fixes 400/200 semantics for "structurally invalid JSON". |
| I-9 | **Missing `record_id` policy** | fail closed: whole request → `HTTP 400` (`INTERIM_MISSING_RECORD_ID_POLICY = "fail_closed_400"`) | A record without an ID cannot be ACKed, which would make the device retry forever; rejecting the request is a demo choice, not contract text. |
| I-10 | **`end_date` may be null** | demo seed emits `null` for open-ended schedules (`INTERIM_SCHEDULE_END_DATE_NULLABLE = True`) | Nullability is `OPEN` in the Decision Register. The demo's choice is not a decision and must not be cited as confirmed. |
| I-11 | **`days` numbering** | `1=Monday … 7=Sunday` (`INTERIM_SCHEDULE_DAYS_CONVENTION`) | This convention appears only in the Phase 1.7.2 design, which is `[PROPOSED]`/`[UNTESTED]`. It is not confirmed firmware contract text. |
| I-12 | **`time` format** | `HH:MM` wall clock in UTC+7 (`INTERIM_SCHEDULE_TIME_FORMAT`) | Same source limitation as I-11. The confirmed contract fixes the `time` key, not its value format. |

**Consequence for real firmware:** if the actual firmware sends a different
request envelope, or a different record shape, it will receive `HTTP 400`, keep
its buffer and retry — potentially indefinitely. **Do not connect real firmware
to this demo** until the request schema and this rejection behaviour are agreed
jointly with the firmware team and recorded as a decision.

**Still `OPEN` and not decided by this demo:** bootstrap token provisioning,
hardware `device_id` format, `FALL`/`FALL_CANCELLED` notification policy, the
exact `unpaired` JSON shape, and multi-time-per-day medication representation.
`end_date` nullability also remains `OPEN`: I-10 records only what the demo
emits, not a resolution. None of these is promoted to `CONFIRMED`.

## 6. Frozen demo data

- One synthetic wearer, one synthetic device, three synthetic schedules, one synthetic event.
- Guardian phone uses the reserved-looking placeholder `+84000000000` (canonical synthetic fixture confirmed by the Project Owner in Phase 2.7.2).
- Every UI surface carries a **DEMO / SIMULATED DATA** label.
- The demo device token is the fixed string `demo-device-token-do-not-use-in-production` and **is not a credential**.
- No real personal, health or telemetry data exists in the repository or the demo database.

## 7. Security posture of the demo

- Binds to `127.0.0.1` only; not intended for any shared or public network.
- The dashboard has **no authentication** — acceptable only because it is local and synthetic. This is a documented deviation, not a design decision.
- `docs_url`, `redoc_url` and `openapi_url` are disabled on the FastAPI app.
- Rejection trace (`sync_rejections`) stores identifiers, record group, reason and timestamp only — never the untrusted payload.
- No API keys, no Supabase project, no cloud credentials.
- Local SQLite files are git-ignored.
- **No production security claim is made.** The approved Option D security model (RLS, four NOLOGIN owners, `private` schema, resolver functions) is not implemented here.
- **Not production-ready:** this is a local, synthetic vertical slice. It must not be deployed, exposed on a network, or connected to real firmware.

## 8. Deviations from Option D (production target)

| Production requirement | Demo state |
| :-- | :-- |
| Supabase PostgreSQL | SQLite |
| Supabase Auth (guardian JWT) | No guardian login |
| RLS with `authenticated` policies | No RLS (single local SQLite file) |
| `private` schema, 4 owner roles, resolver functions | Not implemented |
| RPC `create_medication_schedule_atomic()` + triggers | Not implemented |
| React + Vite frontend | Static HTML/JS |
| FastAPI sync ingestion with `SET ROLE` device identity | Single-process demo, no role separation |

**Production target unchanged:** Option D remains `APPROVED AS TARGET ARCHITECTURE`; this demo is a vertical slice for the 2026-11-26 submission, not an implementation of it.

## 9. Exit criteria for this demo

- [x] `GET /health` and `POST /api/device/sync` implemented
- [x] Flat ACK, HTTP 400/200, per-record rejection implemented
- [x] SHA-256 device token verification implemented
- [x] Seed mechanism producing reproducible synthetic data
- [x] Dashboard showing device status, wearer, schedules, events
- [x] Focused unit tests for contract and persistence layers
- [x] Disjoint sync counters and a metadata-only rejection trace
- [x] `--reset` removes the configured demo database and its SQLite sidecars
- [x] **HTTP layer exercised end-to-end** — automated Uvicorn + `urllib` integration tests (2026-11-25)
- [x] Manual HTTP smoke test — recorded by the Project Owner in Phase 2.3; re-confirmed with `urllib` in Phase 2.7.1 (the `curl` command was not re-run in 2.7.1)

## 10. Verification actually performed

| Check | Result |
| :-- | :-- |
| `python3 -m compileall -q backend` | passed |
| `python3 -m unittest discover -s backend/tests` | **47 tests passed, 0 failed** (41 contract/persistence + 6 HTTP integration) |
| `python3 backend/seed.py --db <tmp> --reset` (twice, with stale `-wal`/`-shm`) | passed; sidecars removed |
| Reset guard on a non-`.db` path | refused as designed |
| Additive migration of a pre-2.2 `sync_logs` table | passed; `duplicates` column added, old rows preserved |
| Pipeline simulation (auth → parse → persist → ACK → config → replay) | passed, 4/4 ACKed, replay added 0 rows and 4 duplicates |
| Automated HTTP integration tests (Uvicorn + stdlib `urllib`, temporary DB) | passed: `/health`, `/api/dashboard`, 200/400/401 cases, ACK, replay, rejection, config handshake |
| Uvicorn server start | **passed** — the test harness starts `.venv/bin/python -m uvicorn` bound to `127.0.0.1` |
| HTTP request via `curl` | **not re-run in Phase 2.7.1**; manual HTTP behavior was recorded by the Project Owner in Phase 2.3 and re-confirmed with `urllib` in Phase 2.7.1 |
| Browser rendering of the dashboard | **headless Firefox renders** in Phase 2.5/2.6 at 1920, 1440, 1280, 1024 and 360 px; interactive browser tests were not run |
| `backend/demo.db` protection during HTTP tests | SHA-256 asserted unchanged before/after the test class |

The HTTP integration tests create and seed an isolated temporary SQLite
database. They do not read from or write to `backend/demo.db`.
