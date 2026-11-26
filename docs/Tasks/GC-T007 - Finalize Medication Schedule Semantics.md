---
kind: task
id: GC-T007
phase: Medication schedule feature
status: Backlog
priority: Medium
depends_on:
decision_state: OPEN
created: 2026-11-21
tags:
  - goldenclock
  - task
---

# Finalize Medication Schedule Semantics

## Objective

Resolve remaining schedule semantics with the firmware team before implementing schedule serialization and management.

## Open questions

- Can `end_date` be null for an indefinite schedule?
- Are date boundaries inclusive?
- Are multiple daily times represented by multiple schedule objects/IDs?

## Acceptance criteria

- [ ] Each question has an agreed answer.
- [ ] JSON field names and types remain consistent with the approved contract unless explicitly amended by both teams.
- [ ] The final semantics are recorded in `project.md`.
