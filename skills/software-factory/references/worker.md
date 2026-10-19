# Worker

A worker is a separate agent session assigned a bounded implementation task by the orchestrator. The worker receives an agreed task, not an open-ended mandate to negotiate product scope with the user. Follow the default isolation procedures below unless the orchestrator supplies an explicit [user-directed workflow](../SKILL.md#user-directed-workflow) exception. Spoken progress reports belong to the orchestrator, not workers.

## Before implementation

- Always work from the task worktree provisioned by the orchestrator at `<repo>/.worktrees/<task-name>`, on branch `<task-name>`. This applies to every task, including documentation-only work and single-worker runs. Verify the assigned directory and branch before task work. If launched elsewhere, stop and notify the orchestrator; never create your own worktree or fall back to the main checkout.
- Before implementation, verify the orchestrator supplied the official task path/URL and populated `TASKS/WIP/YYYY-MM-DD-<task>/brainstorm.md` and `todos.md`. If either is missing or important requirements remain unresolved, stop and notify the orchestrator; do not scaffold or brainstorm a replacement yourself.
- Read project `AGENTS.md`, relevant `PRODUCT/` and `ARCHITECTURE/` documents, the official task, all documents in its WIP directory, and applicable how-we-build guidance. Follow the agreed `todos.md` plan.
- Confirm the task is a coherent, appropriately sized unit. If it is too broad, explain why and ask the orchestrator to split it into official tasks before doing partial work.
- Run task edits, tests, and builds from the assigned worktree. Explicit shared bookkeeping and final integration may target the main checkout; neither authorizes performing the task there. Keep shared status and artifacts visible as required by the task adapter.
- Fill in smaller implementation details as needed. Do not transfer unresolved product or architecture planning to the worker. If a necessary human decision remains, mark the task blocked in the shared task system and notify the orchestrator when possible; do not hold a private question in the worktree.

## Implement and validate

- Follow agreed scope and project invariants. If the proposal directly conflicts with established product/architecture guidance, stop and record the conflict as a blocker; missing documentation alone is not a blocker when reasonable work can be inferred consistently.
- Prefer TDD and a thin, end-to-end tracer-bullet slice where appropriate.
- Run agreed tests, then verify the running product yourself as described in [quality assurance](quality-assurance.md): operate it independently of the tests (click through the UI, run requests by hand, query data directly). Implementation tests alone do not establish product QA.
- Treat code cleanup as part of the work, not a separate decision. Remove dead code, unused aliases/parameters, and duplication you introduce or encounter in your scope; make small correctness improvements without asking. Fix trivial review findings on your best judgment using the same TDD discipline. Never re-raise agreed plan items for approval. Escalate only when something changes architecture shape or product experience, contradicts the agreed plan, or a necessary human decision remains; trivial misjudgments are cheap to correct later.
- Update affected PRODUCT/ and ARCHITECTURE/ docs to match behavior and architecture changes before committing; do not manufacture edits to unaffected documents. Surface material doc changes to the orchestrator; routine doc alignment needs no approval.
- If the user requested a walkthrough, prepare the handoff per [quality assurance](quality-assurance.md) — isolated environment running, seed data loaded, ordered steps with expected results — and stop for user approval instead of integrating.
- Maintain `TASKS/WIP/YYYY-MM-DD-<task>/todos.md`, progress, and visible notes as work proceeds. Put blockers and task status in the main/shared task system, not only in the implementation worktree, so the orchestrator can observe them.
- When tests, QA, or integration fail, keep iterating while making progress. The worker decides whether it is stuck; when it runs out of useful options, mark the task blocked, explain evidence and attempted remedies, and notify the orchestrator.

## Complete

Follow [integration](integration.md): sync current `main`, resolve ordinary conflicts, validate, merge the task branch locally when ready, update visible task/artifact state, and clean up. Keep remote push and publication separate; these are not authorized by local integration.
