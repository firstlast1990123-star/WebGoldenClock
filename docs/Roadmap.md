---
type: project-roadmap
project: GoldenClok
updated: 2026-11-27
tags:
  - goldenclock
  - roadmap
---

# GoldenClok — Roadmap

This roadmap shows the known project sequence. It is a planning view, not approval to begin a phase. Option D (Hybrid) was approved as the **target** production architecture in Phase 1.7.2; that approval does not authorize or imply production implementation. Production Phase 2 remains blocked until security readiness is demonstrated, the unresolved decisions are closed and implementation is explicitly authorized. A separately authorized, reduced Contract Demo has been implemented as a local-only vertical slice; it does not unblock production Phase 2.

## Progress overview

| Stage | Status | Exit condition |
|---|---|---|
| Phase 1 — Project Discovery | **Done** | Repository, environment and initial contract were inspected; initial findings recorded. |
| Phase 1.5 — Architecture Refinement & Contract Correction | **Done** | Known contract errors were corrected; confirmed, provisional, proposed and open items were separated. |
| Workspace Governance | **Done** | `AGENTS.md` and the project logging policy were created. |
| Obsidian Knowledge Workspace | **Done** | Dashboard and task board verified by the Project Owner (GC-T001); roadmap content reconciled in Phase 2.8.1 (Obsidian rendering of the roadmap was not separately re-confirmed). `.obsidian/` remains ignored by Git. |
| Phase 1.6 — Architecture Finalization & Readiness Audit | **Done** | Read-only audit report completed and reconciled at `docs/Architecture/Phase 1.6 - Architecture Readiness Audit.md`. |
| Phase 2 — Contract Demo (reduced, local-only) | **Done (demo only)** | FastAPI + SQLite + static HTML/JS vertical slice implemented and tested (47 automated tests); not production architecture. |
| Git Baseline — Contract Demo | **Done** | 33 reviewed files committed as `ebc288281a8dfc4b9f644cfe2d63ac04ba0c5843` and pushed to GitHub `main` on 2026-11-27; remote `main` verified at the same SHA. |
| Architecture Review & Implementation Authorization | **In progress** | Option D approved as the target architecture (Phase 1.7.2); remaining security/contract decisions and a separate implementation authorization are still pending. |
| Phase 2 — Project Scaffolding | **Blocked** | Only starts after security readiness, closed decisions and explicit implementation authorization; create the approved minimal project skeleton and verification baseline. |
| Database & Guardian Auth implementation | **Planned** | Scope and schema are approved; migrations and auth behavior are tested. |
| Device Integration | **Planned** | Pairing/bootstrap decisions are approved and the device sync contract is implemented without changing it. |
| Guardian-facing product features | **Planned** | Feature scope, UI behavior and acceptance criteria are approved phase by phase. |

## Phase details

### Completed

- **Phase 1 — Project Discovery:** initial repository and environment inspection; initial protocol review.
- **Phase 1.5 — Architecture Refinement:** correction of flat ACK format, sync cadence and other contract details; Supabase PostgreSQL and Supabase Auth recorded as confirmed.
- **Workspace Governance:** `AGENTS.md` and `project.md` working rules established.
- **Phase 2 — Contract Demo (reduced, local-only):** FastAPI sync endpoint, SQLite persistence, synthetic seed, localized dashboard, contract/persistence tests and HTTP integration tests. This is a demo vertical slice, not the production platform.
- **Git Baseline — Contract Demo:** 33 reviewed files committed as `ebc2882` and pushed to GitHub `main` on 2026-11-27; remote `main` verified at the same SHA. The Git operations did not change application source.

### Current preparation

- **Obsidian Knowledge Workspace:** use this Vault for visual navigation, roadmap and task tracking. Keep `project.md` as the canonical progress log.

### Completed gate — Phase 1.6

- Read-only Architecture Finalization & Readiness Audit completed and reconciled.
- True Phase 2 blockers were separated from decisions that can wait until their feature is implemented.
- No production application code, migrations, dependencies or Supabase project were created during the audit.

### Phase 2 gate

Production Phase 2 must not start until security readiness is demonstrated, the unresolved decisions are closed and the Project Owner explicitly authorizes implementation. The Phase 1.7.2 approval of Option D as the target architecture is **not** implementation authorization. Provisional choices must not be treated as approved merely because they appear in a proposal. The reduced Contract Demo does not satisfy or bypass this gate.

## Contract guardrails

- Device sync remains `POST /api/device/sync`.
- ACK remains a flat array of record IDs.
- Malformed JSON/structure: HTTP 400; structurally valid JSON with individually rejected records: HTTP 200 with ACK semantics preserved.
- Device authentication remains separate from Guardian Supabase Auth.
- Time fields remain Unix epoch seconds UTC; medication schedule clock times remain UTC+7.
- Wi-Fi sync cadence and behavior remain as recorded in `project.md`.
- Firmware team owns embedded firmware; the Web team implements only the Web/API integration.

See [[project|official progress log]] and [[docs/Decisions/Open Decisions|open decisions]].
