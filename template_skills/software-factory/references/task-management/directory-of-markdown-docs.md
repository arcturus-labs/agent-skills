# Markdown task-directory adapter

Use this as the default only when the project has no existing task system or the user chooses it. The directory must remain useful without a Kanban UI.

## Layout

```text
BACKLOG.md                 # root quick-capture list; not official tasks
TASKS/
  KANBAN/                  # official task cards and board state
  PLANNING/                # tasks being planned: <task>/ (undated) with brainstorm.md + todos.md
  WIP/                     # dispatched tasks: YYYY-MM-DD-<task>/ (dispatch date), planning and progress artifacts
  COMPLETE/                # completed task artifacts/outcomes, same dated names
```

For a sufficiently complex project, replace `BACKLOG.md` with a `BACKLOG/` directory: `GENERAL.md` as the general dumping ground, plus one topical file per area the user wants to keep separate (e.g. one per major component). Same quick-capture rules apply to every file in the directory; this is purely an organizational split, not a second task system.

Use project-specific IDs and filenames for official cards. Follow the [shared local artifact lifecycle](README.md#local-task-artifacts--every-task-system) for planning, dispatch, and completion, with the exact current directory linked from the card.

## Task cards

A card should identify the task, describe the desired outcome and acceptance criteria, and expose status. Optional frontmatter can include type, board order/priority, created/touched timestamps, source issue, tags, status history, parent/child links, and prerequisites. Use only fields that are useful and maintainable; keep schemas documented. Bulleted checkboxes are suitable for actionable steps. Put instructions in templates reminding workers to maintain checklists and status.

Settle the Markdown schema during setup. If the project uses the Obsidian Kanban Board skill, load the installed `obsidian-kanban-board` skill for its schema, ordering, and update rules rather than inventing another schema here. Preserve managed metadata and status history. Ensure a visible `blocked` state and a place for comments or rationale (card body, linked notes, or activity log).

## Shared state and worktrees

Implementation branches/worktrees isolate code, not operational state. Task status, blockers, comments, WIP planning/progress artifacts, and worker registry updates must be written where the orchestrator can see them from the main checkout; do not leave the only copy inside a worker worktree. Avoid concurrent edits to the same task or shared planning files.

The official task card is the board-level record. WIP `todos.md` is the detailed ordered checklist, and `outcome.md` records completion, evidence, and important decisions. On completion, move the artifacts from `TASKS/WIP/YYYY-MM-DD-<task>/` and the card from `TASKS/KANBAN/<task>.md` into `TASKS/COMPLETE/YYYY-MM-DD-<task>/` so completed cards do not accumulate on the live board. Update relative links in the moved card and artifacts so they still resolve.
