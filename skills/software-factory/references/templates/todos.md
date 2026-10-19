# Task execution: <task title>

Official task: <path or URL>
Planning directory: `TASKS/PLANNING/<task>/` (becomes `TASKS/WIP/YYYY-MM-DD-<task>/` at dispatch; the orchestrator updates this line then)
Worker/session: <assigned identity>
Worktree: `<repo>/.worktrees/<task-name>` (provisioned by orchestrator)
Branch: `<task-name>`
Base commit: <committed main SHA>

Orchestrator: copy this template unchanged to `TASKS/PLANNING/<task>/todos.md` when planning begins. Only after the user explicitly indicates brainstorming is complete, replace placeholders and fill in a descriptive, ordered checkbox plan, including nested steps where useful. Worker: track progress directly in the checklist. Check off completed items and append a short update after ` ~ `, for example: `- [x] Add activation endpoint. ~ Validation tests pass.` Add a separate details section only when needed and reference it from the checklist item. The orchestrator and user should already have clearly outlined the requirements. Work within that agreed scope; escalate omitted requirements, contradictions, or necessary human decisions rather than reopening settled items. Branch/worktree steps below are defaults; follow any explicit user-directed exception supplied by the orchestrator.

## Checklist

- [ ] Review task plan, project instructions, PRODUCT/, and ARCHITECTURE/.
- [ ] Create TASKS/PLANNING/<task>/brainstorm.md and TASKS/PLANNING/<task>/todos.md, mention the directory in the official task, perform brainstorming and todo list generation, and update the paths here (orchestrator).
- [ ] At dispatch, move the directory to TASKS/WIP/YYYY-MM-DD-<task>/ (dispatch date), and update the path here, in brainstorm.md and in the official task's mention (orchestrator).
- [ ] Review all TASKS/WIP/YYYY-MM-DD-<task> documents (worker).
- [ ] Before worker launch: verify clean, committed main; create the matching task branch/worktree; verify planning documents in it; launch worker there (orchestrator).
- [ ] Verify assigned worktree and branch before task edits; stop if launched elsewhere, never create a worktree or work from main (worker).
- [ ] Confirm the agreed scope is manageable; escalate if further decomposition is needed.
- [ ] <Implement each vertical slice using test-driven development, with acceptance criteria and nested checkboxes as needed.>
- [ ] <Relevant tests and checks.>
- [ ] <Independent product QA steps and expected observable results.>
- [ ] Sync current main, resolve conflicts, and repeat relevant validation.
- [ ] If requested, prepare the user walkthrough and obtain explicit approval before integration.
- [ ] Merge locally when ready.
- [ ] Record outcome, hands-on usage instructions, and verification evidence; move artifacts to TASKS/COMPLETE/YYYY-MM-DD-<task>/ and update the official task's status and links.
- [ ] For Markdown tasks, archive the card per the task-management adapter.
- [ ] Clean up worktree.

## Blockers (only when truly blocked)

- <Reason, attempts, and decision/prerequisite needed; also update shared task state.>
