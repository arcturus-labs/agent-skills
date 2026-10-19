# Integration and completion

The worker owns routine integration for its task. There is no routine user approval gate or central integration slot. Each task should remain identifiable and reasonably easy to undo. A requested user walkthrough adds an explicit approval gate before integration; see [quality assurance](quality-assurance.md). Honor explicit [user-directed workflow](../SKILL.md#user-directed-workflow) exceptions to branch/worktree procedures.

1. Finish the agreed implementation, tests, and independent QA.
2. Sync the task branch with current `main`; resolve ordinary conflicts in the task branch.
3. Run the relevant validation again after conflict resolution. If a check fails, fix and retry while making progress. If blocked, record why in the shared task system and notify the orchestrator.
4. Merge the completed task branch into local `main` when ready. Do not push remotely, publish, deploy, or release unless separately authorized.
5. Write/update the outcome artifact in the main checkout. Include a concise hands-on walkthrough: actual setup/run commands, representative inputs, and how to inspect the resulting product behavior. Keep it reproducible and separate from the test report. For every task system, move the task's WIP directory to `TASKS/COMPLETE/YYYY-MM-DD-<task>/`, keeping its dispatch-date prefix; update document paths and the official task's status and artifact links. Follow the [Markdown adapter](task-management/directory-of-markdown-docs.md) for moving completed local cards; external issues/tickets remain in their native system.
6. Commit bookkeeping/artifact changes when appropriate and clean up the task worktree/branch according to project policy.

If integrating changes requires a product, architecture, or scope decision, stop and mark the task blocked rather than guessing. Keep the task branch/change identifiable so the user can revert or repair it later; reversibility is best-effort, not a guarantee.
