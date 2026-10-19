# Task-management contract

The factory core is independent of any task application. During setup, identify the user's system and map its capabilities; do not silently assume Markdown, GitHub, or Jira. An adapter should tell the orchestrator how to list/read/create/update tasks and record descriptions, status, and visible comments/activity. Prefer support for priorities, subtasks, dependency links, and a blocked state, but treat these as optional capabilities. If the system is missing or underspecified, tell the user and define the adapter before relying on it.

## Local task artifacts — every task system

Official tasks may live anywhere; durable agent context always lives locally:

- **Planning:** create undated `TASKS/PLANNING/<task>/` with `brainstorm.md` and `todos.md`; immediately link it from the official task.
- **Dispatch:** move it to `TASKS/WIP/YYYY-MM-DD-<task>/` using the local dispatch date. Update paths in the documents and official task, and commit before worktree provisioning. Keep official task IDs, branch names, and worktree names undated.
- **Completion:** move the artifacts to `TASKS/COMPLETE/YYYY-MM-DD-<task>/` with the same dispatch-date prefix. Include `outcome.md`, verification evidence, and practical usage instructions; update the official task's link and status.

These directories are required for Markdown, GitHub, Jira, and any other task system; they are not an alternative task board. The [orchestrator](../orchestrator.md) owns planning and dispatch. Keep progress, blockers, and artifacts visible from the main checkout rather than stranded in a worker's worktree. Markdown card creation and archival are specific to the [Markdown adapter](directory-of-markdown-docs.md); external tasks remain in their native system.

## Shared concepts

- **Quick capture:** root `BACKLOG.md` (or, for a sufficiently complex project, a `BACKLOG/` directory with `GENERAL.md` plus topical files) is a lightweight plain bullet list, not the official task board. It is acceptable to capture an idea without creating a fully specified issue. When promoting an item to the official system, delete it from the backlog file rather than checking it off, so the file doesn't fill up with dead entries; link/reference the official task from wherever the idea landed.
- **Official tasks:** live in the selected task system. The orchestrator reviews both the official system and quick-capture backlog when choosing work.
- **Ready:** no known blocker/dependency; user and orchestrator agree requirements are explicit enough for isolated implementation. The official task mentions its planning directory (`TASKS/PLANNING/<task>/`, or the dated `TASKS/WIP/YYYY-MM-DD-<task>/` once dispatched), containing populated `brainstorm.md` and `todos.md`. These local planning artifacts are required even when the official task lives in GitHub, Jira, or another system. Promotion from backlog alone does not establish readiness.
- **Blocked:** the task cannot proceed without an external decision or missing prerequisite. Record the reason and requested decision visibly; a task status alone is insufficient when a comment/description can explain it.
- **In progress:** assigned to an active worker/session. Ownership and liveness may be tracked outside the task system, but must be visible to the orchestrator and human.
- **Complete:** implementation and agreed validation are complete and the task links to its outcome/artifacts.

Task assignment/worker liveness is factory metadata separate from task-system fields, even if the task system also supports assignment. Do not make a task's status depend on state hidden in an agent transcript.

## Missing capabilities

When a system lacks explicit priority, dependencies, subtasks, or comments, the orchestrator makes cautious best-effort inferences from task text and activity. There are usually few active tasks, so simple judgment is acceptable. State the limitation to the user, make important inferred relationships/blockers visible where possible, and invite correction. Do not pretend inferred metadata is native or authoritative.

If there is no existing task system, use the [Markdown task-directory adapter](directory-of-markdown-docs.md). For GitHub and Jira, these files are discussion placeholders, not complete adapters: [GitHub](github.md), [Jira](jira.md).
