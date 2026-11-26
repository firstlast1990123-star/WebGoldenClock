---
kind: task
id: GC-T005
phase: Guardian Authentication
status: Backlog
priority: Medium
depends_on:
decision_state: PROPOSED
created: 2026-11-21
tags:
  - goldenclock
  - task
---

# Decide Guardian Login Method

## Objective

Approve the Guardian sign-in method for V1.

## Current proposal

Email and password has been proposed, but has not been approved.

## Acceptance criteria

- [ ] Review user experience, security, verification and operational cost.
- [ ] Explicitly approve or reject the proposal.
- [ ] Record the decision in `project.md` and [[docs/Decisions/Open Decisions]].

## Timing

Must be resolved before implementing Guardian Auth; it is not assumed to block the read-only Phase 1.6 audit.
