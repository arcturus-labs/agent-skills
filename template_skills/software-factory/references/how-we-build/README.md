# How we build

These are starting recommendations, not universal laws. During setup, discuss the user's practices and adapt or replace this guidance. Prefer TDD where practical, thin end-to-end tracer-bullet slices over completing one architectural layer at a time, and useful logging that makes failures diagnosable.

## Common project affordances

Agree on reliable run, test, QA, and build commands. A root-level `scripts/` directory is the recommended project convention: one language-agnostic, makefile-like index of everything the application can do, so neither humans nor agents must remember or rediscover commands. It is distinct from scripts that implement this skill.

- `scripts/README.md`: terse one-line description per script; update it with every script add/change.
- Layout: the top level holds only runnable `.sh` entry points plus `README.md`; supporting implementation belongs in `scripts/lib/`, which may use subdirectories for segregation. Keep entry points thin and readable.
- `scripts/run.sh`: starts all repo services in the background (installing prerequisites if missing, reusing already-running services). `run.sh stop` stops them. New services join the same script. Environment overrides (e.g. alternate home directories) via env vars; the script reads `.env` without overriding already-set variables.
- Reference the directory from `AGENTS.md` so injected instructions point at it.

For substantial work:

1. Confirm the intended user-visible behavior and acceptance criteria.
2. Design a small vertical slice through the relevant layers.
3. Add/update tests alongside implementation; prefer tests first where appropriate.
4. Exercise the running product independently of the code that implemented it.
5. Keep docs and task checklists in sync.

## Domain guidance

One file per codebase type. Each covers its preferred stack, structure, and how to verify the running product. Add a file when a project introduces a type not listed here; do not guess silently.

- [Web frontend](web-frontend.md) — browser UI over an API (Vite + React + TypeScript).
- [Backend service](backend-service.md) — local HTTP/JSON service with layered architecture and embedded persistence.
- [Native app](native-app.md) — OS-native application.
- [Mac applications](mac-applications.md) — SwiftUI/AppKit architecture, AppleScript/SDEF planning, and isolated AX-driven QA.

Read [quality assurance](../quality-assurance.md) for mandatory product verification and optional user-attended walkthroughs. Codebase-specific design and agent-integration decisions belong in the references above.
