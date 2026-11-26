---
type: project-dashboard
project: GoldenClok
updated: 2026-11-25
tags:
  - goldenclock
  - dashboard
---

# GoldenClok — Project Hub

> [!info] Current stage
> **Contract Demo implemented — production Phase 2 remains blocked.** Phase 1, Phase 1.5 and the Phase 1.6 audit report have been completed and reconciled at [[docs/Architecture/Phase 1.6 - Architecture Readiness Audit|Phase 1.6 Report]]. A reduced, local-only Contract Demo (FastAPI + SQLite + static HTML/JS) is implemented and tested; the Phase 2.6 Vietnamese dashboard has been visually approved by the Project Owner. Option D (Hybrid) was approved as the **target** production architecture in Phase 1.7.2, but production implementation has not started and remains subject to security readiness, unresolved decisions and separate implementation authorization. The production stack (Supabase, Auth, RLS, React) remains not implemented.

## Project snapshot

| Item | Current state |
|---|---|
| Product | GoldenClok wearable and companion Web platform for elderly care |
| Your responsibility | Full-stack Web platform, API, database, authentication and device integration |
| Firmware responsibility | Separate team; do not implement ESP32/A7680C firmware here |
| Database | Supabase PostgreSQL — **CONFIRMED** (production target; demo uses SQLite) |
| Guardian authentication provider | Supabase Auth — **CONFIRMED** (production target; not implemented) |
| Backend | FastAPI — **PROVISIONAL** (Contract Demo uses FastAPI) |
| Frontend | React + Vite + TypeScript — **PROVISIONAL** (demo uses static HTML/JS) |
| UI styling | Tailwind CSS — **PROVISIONAL** (demo uses plain CSS) |
| Application code | **Contract Demo only** — production app not started |
| Database migrations | Not started (SQLite demo schema only) |
| Automated tests | 47 — 41 contract/persistence + 6 HTTP integration |

## Quick navigation

- [[project|Official project progress log]]
- [[AGENTS|Agent working rules]]
- [[README|Repository README]]
- [[docs/Roadmap|Project roadmap]]
- [[docs/Tasks/Task Board.base|Task board]]
- [[docs/Decisions/Open Decisions|Open decisions and proposals]]

## Current priorities

1. Obsidian Dashboard and Task Board have been verified by the Project Owner ([[docs/Tasks/GC-T001 - Verify Obsidian Dashboard and Task Board|GC-T001: Done]]); roadmap content was reconciled in Phase 2.8.1 (Obsidian rendering of the roadmap was not separately re-confirmed).
2. Project Owner reviews the reconciled [[docs/Architecture/Phase 1.6 - Architecture Readiness Audit|Phase 1.6 Architecture Readiness Report]] and decides on the provisional Tech Stack ([[docs/Tasks/GC-T003 - Review Phase 1.6 Report and Decisions|GC-T003]]).
3. Authorize production Phase 2 scaffolding only after security readiness is demonstrated, the unresolved decisions are closed and implementation is explicitly authorized ([[docs/Tasks/GC-T004 - Approve Architecture and Authorize Phase 2|GC-T004]]).
4. The local-only Contract Demo is verified by automated tests and manual smoke checks; it is not production architecture and must not be exposed publicly. See [[project|project.md]] for the Phase 2.7.1 record.

## Task board

![[docs/Tasks/Task Board.base#Board]]

## Decision status guide

| Label | Meaning |
|---|---|
| **CONFIRMED** | Explicitly confirmed by the Project Owner or agreed contract |
| **PROVISIONAL** | Candidate selected for evaluation; not finally approved |
| **PROPOSED** | Proposal awaiting review and approval |
| **OPEN** | No decision has been made |

> [!warning] Source of truth
> `project.md` remains the **official and only project progress log**. This dashboard, roadmap and task board are navigation and planning views; they do not replace the approved Firmware ↔ Web contract or the official progress history.
