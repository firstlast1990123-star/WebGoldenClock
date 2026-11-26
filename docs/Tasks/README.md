---
type: task-board-guide
project: GoldenClok
tags:
  - goldenclock
  - tasks
---

# Task Board — How to use

Open [[docs/Tasks/Task Board.base|Task Board]]. It has a Kanban view and a table view backed by individual Markdown task notes.

## Status values

- `Backlog` — known work, not ready to start.
- `Todo` — ready to be picked up.
- `In progress` — currently being worked on.
- `Blocked` — cannot proceed until a dependency or approval is satisfied.
- `Done` — acceptance criteria have been verified.

## Creating a task

1. Duplicate [[docs/Tasks/Task Template]].
2. Give the file a unique ID, for example `GC-T009 - Short task title`.
3. Fill in the YAML properties at the top. Keep `kind: task` so the note appears in the Base.
4. Set `status` to one of the five exact values above.
5. Add acceptance criteria and evidence in the note body.

## Updating a task

- Move a card between Kanban columns to update its `status`, or edit the status property in its note.
- Mark a task `Done` only after its acceptance criteria are checked.
- Use `depends_on` to record prerequisite task IDs. Do not mark a blocked task as `Todo` while its dependency is unresolved.
- Keep sensitive information out of task notes because this repository is public.

`project.md` remains the official project progress log; task notes are operational work items, not a replacement history.
