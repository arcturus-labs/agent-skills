---
name: software-factory
description: Use when setting up a software project, planning work, coordinating implementation agents, or maintaining shared task and project guidance.
---

# Software factory

A reusable, project-local workflow for setting up a project, planning and tracking work, coordinating implementation workers, independently validating the product, and integrating completed tasks. This template skill is normally symlinked into a project from a project-specific worktree branch and customized there; do not assume a global installation or a particular harness or task system.

## Start here

1. Read the relevant project instructions (`AGENTS.md`), `PRODUCT/`, `ARCHITECTURE/`, task-system documentation, and this skill's applicable references.
2. For first-time setup, follow [setup](references/setup.md). Reconcile existing project documentation; do not overwrite useful material blindly.
3. For ongoing work, use [orchestrator](references/orchestrator.md). For an assigned implementation task, use [worker](references/worker.md). For integration, see [integration](references/integration.md). For periodic reviews, see [audits](references/audits.md).
4. Load the matching task-management, agent-harness, and build/QA references. If an integration is missing or underspecified, tell the user and agree on it before proceeding; do not pretend a placeholder is a working adapter.

## Planning pipeline

Every task system uses local `TASKS/PLANNING/`, `TASKS/WIP/`, and `TASKS/COMPLETE/` directories for durable agent context. The official task may live in Markdown, GitHub, Jira, or elsewhere; it links to these artifacts. See [task management](references/task-management/README.md) for the shared lifecycle.

1. Capture scrap ideas in root `BACKLOG.md` (or a `BACKLOG/` directory, for a project complex enough to warrant per-topic files).
2. Promote selected ideas to official tasks in `TASKS/KANBAN/`, GitHub, Jira, or the chosen task system. Promotion does not mean ready for a worker.
3. When fleshing out a task, the orchestrator creates `TASKS/PLANNING/<task>/`, named after the task and undated, with `brainstorm.md` and `todos.md` initially copied unchanged from the planning and execution templates. Immediately mention this directory in the official task itself (markdown card, GitHub issue, Jira ticket, or wherever the task lives). Develop the brainstorm with the user, but leave `todos.md` unchanged until the user explicitly indicates brainstorming is complete.
4. Gather the user's initial details, then iterate appended Q&A rounds in `brainstorm.md`; the user answers inline and the orchestrator inspects relevant code. Continue until both agree the requirements, acceptance criteria, and QA plan are explicit enough for isolated implementation.
5. After the user indicates brainstorming is complete, the orchestrator resolves `todos.md` placeholders and writes a detailed, ordered checkbox plan, then dispatches: it moves the directory to `TASKS/WIP/YYYY-MM-DD-<task>/` (the date is the dispatch day, fixed from then on and kept when archived), updates the directory mention on the official task, and verifies a clean, committed `main` including the moved planning documents. It creates `.worktrees/<task-name>` on matching branch `<task-name>` and launches the worker in that worktree with the official task reference and both WIP documents. Under the default workflow, implementation requires these populated documents and an orchestrator-provisioned worktree.

See [orchestrator](references/orchestrator.md) for the file-based brainstorming procedure and dispatch checks. Use the `brainstorm.md` and `todos.md` templates for the task-local documents.

## Operating principles

- The orchestrator owns the human conversation, task selection, planning, dispatch, and coordination. Workers implement bounded, agreed tasks.
- Plan substantial product, scope, and architecture uncertainties with the user before dispatch. Record the Q&A in the required `brainstorm.md` in the task's planning directory (`TASKS/PLANNING/<task>/`, dated and moved to `TASKS/WIP/` at dispatch) and the agreed execution plan in `todos.md`. Workers may resolve smaller implementation details, but should not reopen user-level planning; if a human decision is genuinely needed, they mark the task blocked in the shared task system and notify the orchestrator when possible.
- Once the user authorizes autonomous execution, keep selecting and dispatching ready tasks until told to stop. Periodically inspect in-flight work and surface blockers. Default to at most three concurrent work items unless the user chooses another limit. Avoid overlapping write scopes.
- Keep the human and orchestrator looking at the same operational state: task status, blockers, progress, ownership/liveness, and outcomes must not be hidden inside a worker session or worktree.
- Prefer TDD and thin end-to-end tracer-bullet slices, adapted to the user's project and preferences. Verify the actual product independently of the implementation; tests and code review alone are not product QA.
- `PRODUCT/` and `ARCHITECTURE/` are authoritative descriptions of existing and planned behavior and architecture, not planning artifacts.
- Structure `ARCHITECTURE/` as terse, noun-based component documentation. For each component, capture its purpose, prominent technology choices, important APIs, relevant data schemas, and class/extension hierarchy. See [setup](references/setup.md) and the [component template](references/templates/architecture-component.md); avoid source-code tours and redundant prose.
- Workers own task implementation, validation, and routine integration. Automated checks may reject work; workers should fix and retry while making progress, and mark the task blocked when stuck. Routine local integration does not authorize remote push or publication.
- Unless the user explicitly chooses another workflow, every task worker works in its own Git worktree, including documentation-only tasks and single-worker runs. The orchestrator alone provisions `<repo>/.worktrees/<task-name>` on branch `<task-name>` from clean, committed `main` and starts the worker there. Workers do not create worktrees; no shared-checkout fallback. If Git isolation cannot be established, block dispatch. Keep task bookkeeping visible and document completed work.
- Strong defaults are adaptable. Ask during setup about task system, harness, concurrency/subworkers, engineering practices, and QA affordances.

## User-directed workflow

This workflow is guidance, not a reason to refuse an explicit user choice. If the user requests a different workflow, including ad hoc work, briefly note the normal recommendation and follow their choice without requiring repeated confirmation. The override applies to the chosen task and the corresponding procedures in this skill's references; it does not waive safety, privacy, or unrelated project constraints.

When the user explicitly requests direct-on-main execution:

- Verify the checkout is on `main` and inspect existing changes before editing.
- Preserve unrelated staged, unstaged, and untracked work. Never reset, stash, overwrite, or include it in a commit without permission.
- Skip worktree/branch provisioning, the clean-main provisioning gate, branch merging, and worktree cleanup. Do not dispatch overlapping writers into the shared checkout.
- Keep the agreed scope, task records, tests, product verification, and outcome reporting. Record the user's workflow choice.
- This choice does not authorize remote pushes, publication, deployment, or destructive operations.

## References

- [Setup](references/setup.md)
- [Orchestrator](references/orchestrator.md)
- [Worker](references/worker.md)
- [Integration](references/integration.md)
- [Audits](references/audits.md)
- [Quality assurance](references/quality-assurance.md)
- [Task management](references/task-management/README.md)
- [Agent harnesses](references/agent-harness/README.md)
- [How we build](references/how-we-build/README.md)
- [Templates](references/templates/README.md)
- [Script boundary](scripts/README.md)
