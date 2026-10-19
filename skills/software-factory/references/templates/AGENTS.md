# Project agent instructions

Project-specific instructions for all agents working in this repository. Keep these concise, actionable, and consistent with `PRODUCT/` and `ARCHITECTURE/`.

## Software practices

- The `software-factory` skill owns workflow guidance: planning, task tracking, delegation, worktrees, and integration. Follow it alongside this project's substantive constraints.
- Keep the skill symlinked into this repository (for example `.agents/skills/software-factory`) and gitignored; never vendor a copy into the consuming repository.
- Commit skill changes in the repository where the skill actually lives, not in the consuming repository.

## Spoken progress reports

On macOS, only the orchestrator uses `say`, not workers. Speak a short status phrase after roughly ten internal tool/thinking turns since the latest user message; space further updates similarly during longer stretches. Also announce worker completion and blockers the orchestrator cannot resolve. Use `say "<repo short name>: <brief status>"`, not lengthy narration. See the skill's orchestrator reference for the full convention.

## Invariants and conventions

- [Project rules, compatibility constraints, security/privacy requirements]

## Structure and architecture

- [Important directories/modules and where changes belong]

## Commands

- Run the project: `[command]`
- Run tests: `[command]`
- Other useful checks/data setup: `[command]`

## Logging and debugging

- Consult root `scripts/` first; its README indexes runnable operations. [How to inspect useful logs and diagnose failures; do not expose secrets]

## QA — required

Describe how to operate and observe the actual product independently of the implementation. Include required environment/data, scripts or accessibility/test selectors, and visual verification steps. Passing tests or reviewing code alone is not product QA. If independent QA cannot be performed for a task, mark it blocked and report what is missing.
