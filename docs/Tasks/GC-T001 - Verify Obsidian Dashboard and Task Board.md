---
kind: task
id: GC-T001
phase: Obsidian Knowledge Workspace
status: Done
priority: Medium
depends_on:
decision_state: CONFIRMED
created: 2026-11-21
tags:
  - goldenclock
  - task
---

# Verify Obsidian Dashboard and Task Board

## Objective

Confirm that the new project hub, roadmap and embedded Bases Kanban board render correctly in Obsidian 1.15.1.

## Scope

- Open `docs/Home.md` in Obsidian.
- Confirm links to `project.md`, `AGENTS.md`, Roadmap and Open Decisions resolve.
- Confirm the embedded `Task Board.base` displays its Kanban columns and task cards.
- Open the Task Register view and check the task properties.
- Confirm `.obsidian/` remains ignored by Git.

## Acceptance criteria

- [x] Dashboard renders without broken links.
- [x] Kanban view shows Backlog, Todo, In progress, Blocked and Done columns.
- [x] The task cards have the expected statuses.
- [x] Table view shows task IDs, phases, statuses and priorities.
- [x] `git status --short --untracked-files=all` does not list `.obsidian/`.

## Verification

Verified by Project Owner: Dashboard (`docs/Home.md`) and Task Board (`docs/Tasks/Task Board.base`) render and display all tasks properly in Obsidian. (Note: Roadmap has not been separately verified).
