# Quality assurance

Tests establish that the code behaves. QA establishes that the product works: operate the running product independently of its implementation and observe real behavior. Tests alone are never product QA.

Product verification is mandatory for every task. A user-attended walkthrough is optional; for a large task, the orchestrator asks whether the user wants one. When the user says "show me" or otherwise requests a walkthrough, record an explicit approval gate in the task plan.

## Plan verification

Before implementation, record representative user journeys, observable success/failure behavior, required data, and independent operating affordances in the task plan. Put reusable project commands and selectors in `AGENTS.md`. Prefer scripted interaction that operates the actual product and asserts resulting state; use human interaction where automation cannot verify the experience. For visual/layout changes, capture relevant application/window screenshots and inspect them, avoiding unrelated desktop content.

## The worker's own verification

Every task, whether or not the user asked for a walkthrough:

1. TDD is the first line of defense: failing test first, then implementation.
2. After all tests pass, verify the running product yourself, differently from the tests: open the UI and click through it, run curl requests by hand, query the database directly. Do not just re-run the test suite under another name.
3. If this verification fails, fix and repeat. Only work the user explicitly asked to see waits for user QA.

## The user walkthrough

When the user requested a walkthrough, the worker prepares a reproducible handoff and stops; the orchestrator presents it, relays findings, and waits for explicit approval before integration. The walkthrough shape depends on what changed:

- **Service changes:** start the service in an isolated QA environment (separate data directory and port, never production), seed representative data, and give the user curl commands with expected responses. Prefer the project's `scripts/` entry points (`run.sh`, `seed.sh`) with environment overrides.
- **UI changes (web or native):** same isolated setup and seed data, then open the app at the relevant screen and give click-by-click instructions: what to click, what to watch for, what correct looks like. Never point QA at production assets.
- **Anything else:** match the medium to the change — SQL statements and how to open the database for a data change, commands and expected output for tooling, and so on.

Every handoff includes:

- Exact commands to start, seed, inspect, and stop the QA environment (or the open app's location, if already running).
- The walkthrough itself: ordered steps with expected observable results.
- Evidence from the worker's own verification: what was operated, what was observed, and the key outputs.
- Limitations: what was not covered and why.

The worker leaves the QA environment running (or provides exact restart commands), addresses findings, re-runs affected checks, and returns for another round. Merge waits on the user's explicit approval.

Findings normally travel through the orchestrator as a summary. When the user would rather interrogate the worker directly — why it chose an approach, what it observed, what it would do differently — offer direct session contact only through a currently verified safe harness handoff with exclusive, sequential session ownership. Otherwise relay the user's messages and the worker's replies verbatim. See [agent-harness](agent-harness/README.md) for the route your harness supports. Anything decided either way still belongs in the planning documents.

If QA is not feasible — missing access, instrumentation, environment, or acceptance criteria — mark the task blocked and say what is needed. Do not relabel tests as QA.
