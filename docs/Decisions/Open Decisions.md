---
type: decision-register
project: GoldenClok
updated: 2026-11-21
tags:
  - goldenclock
  - decisions
---

# GoldenClok — Decision Register

This page collects decisions that still need review. It does not approve them. `project.md` remains the canonical historical record; when the Project Owner makes a decision, record it there and update this register.

## Confirmed foundations

| Topic | Decision | Status |
|---|---|---|
| Database | Supabase PostgreSQL | **CONFIRMED** |
| Guardian authentication provider | Supabase Auth | **CONFIRMED** |
| Device sync endpoint | `POST /api/device/sync` | **CONFIRMED** |
| ACK format | Flat array of record IDs | **CONFIRMED** |
| Device/Guardian auth separation | Device token is separate from Guardian Auth | **CONFIRMED** |
| Retention | HR 7 days, medication records 7 days, events 30 days; schedules are not auto-deleted | **CONFIRMED** |

## Provisional and proposed choices

| Topic | Current candidate | Status | When it must be resolved |
|---|---|---|---|
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2.0 Async + Alembic | **PROVISIONAL** | Before Phase 2 scaffolding |
| Frontend | React + Vite + TypeScript | **PROVISIONAL** | Before Phase 2 scaffolding |
| Styling | Tailwind CSS | **PROVISIONAL** | Before frontend implementation |
| Guardian login | Email + password | **PROPOSED** | Before Guardian Auth implementation |
| Device bootstrap | Factory-provisioned pre-shared secret or one-time QR activation | **PROPOSED** | Before device pairing implementation |
| Maximum records per sync | 200 records per request | **PROPOSED** | Before defining request limits |
| Database connection | Session Pooler for API and Direct connection for Alembic | **PROPOSED** | Before database connectivity/migrations |
| Data schema | Ten entities identified in Phase 1.5 | **Draft; approval not recorded** | Before creating migrations |

## Open decisions

| Topic | What is unresolved | Must be resolved by |
|---|---|---|
| Initial device bootstrap | How an unpaired device securely receives its first token | Before device pairing implementation |
| `device_id` | Hardware identifier format and provisioning method | Before device provisioning/pairing implementation |
| Medication schedule dates | Whether `end_date` can be null and how date boundaries are interpreted | Before medication schedule implementation |
| Multiple medication times | Whether each daily time is a separate schedule object/ID | Before schedule serialization and UI implementation |
| `FALL` / `FALL_CANCELLED` notifications | Guardian-facing notification policy and timing | Before alert UX implementation |
| Web Push | Whether it belongs in V1; current sync model does not guarantee real-time delivery | Before promising real-time alerts |
| Config response when unchanged | Whether server returns `config: null`, empty object `{}`, or omits `config` when versions match | Before sync response serialization |

## Rules for changing a decision

1. Do not promote a proposal or provisional choice to **CONFIRMED** without explicit Project Owner approval.
2. Do not implement an **OPEN** item by guessing.
3. When a decision is approved, update `project.md` with its date, rationale and scope; then update this page.
4. Do not change the Firmware ↔ Web JSON contract without a joint, explicit approval from the responsible teams.
