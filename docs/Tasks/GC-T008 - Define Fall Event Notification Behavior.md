---
kind: task
id: GC-T008
phase: Fall event and guardian notifications
status: Backlog
priority: Medium
depends_on:
decision_state: OPEN
created: 2026-11-21
tags:
  - goldenclock
  - task
---

# Define Fall Event Notification Behavior

## Objective

Agree on what the guardian sees when `FALL` and `FALL_CANCELLED` events are received, without promising delivery that the V1 sync architecture cannot guarantee.

## Acceptance criteria

- [ ] Event persistence and incident presentation are distinguished.
- [ ] The meaning of `FALL_CANCELLED` is agreed while preserving both event records.
- [ ] Dashboard indication and any push-notification scope are explicitly decided.
- [ ] `events.sms_sent` is never presented as confirmed SMS delivery.
- [ ] Decisions are recorded in `project.md`.

## Timing

Resolve before implementing guardian-facing fall alert behavior.
