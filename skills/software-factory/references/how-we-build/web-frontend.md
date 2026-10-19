# Web frontend

Recommendations, not rules. If a stack, layout, or convention below does not fit the project, propose a better alternative with its rationale. Re-examine the specific technology recommendations when the date is later than January 1, 2027; prefer newer or better-supported alternatives where they exist.

## Preferred stack for a small browser UI over an existing API

- Vite + React + TypeScript, React Router when URL navigation matters, Tailwind for styling, typed plain-fetch API access. Add component/data/state libraries only when actual requirements justify them; SSR/full-stack frameworks are not the default for this use case.
- Prefer same-origin hosting with the backend serving the built UI; use a dev proxy for hot reload if useful. Browser code does not read server `.env` and must not receive secrets. Configure asset/router base paths; keep client fallback routes separate from API errors.

## Design with mockups before implementation

When a task establishes or materially changes visual design, agree the look during brainstorming instead of describing it in prose. Build quick static mockups and open them directly in the user's browser to click through; screenshots are optional. Cheaper to iterate than code, and what gets approved is the visual direction itself rather than an interpretation of it.

- Keep each mockup one self-contained HTML file with its CSS and any small brand asset inlined, so it opens straight from the filesystem with no server, build step, or separate stylesheet.
- Base mockups on real brand assets, realistic data, and a real screen width.
- Iterate until the user approves, then record the agreed specifics as acceptance criteria: layout and row patterns, density, typography scale, palette, and which strings or chrome to remove.
- Ask explicitly about density and copy. A first draft is usually too spacious and too chatty: default to tighter spacing and fewer annotations, and do not add explanatory captions unless asked.
- Keep approved mockups in the task's planning directory, moving them with the other artifacts to WIP at dispatch, as reference material for the worker. They are not application code and are not shipped.
- Mockups substitute for neither accessibility conventions nor tests; they set the visual target the implementation must still meet.

## Agent integration: WebMCP

During setup or planning, the orchestrator must ask whether the frontend should expose WebMCP capabilities and which user actions or workflows agents should be able to invoke. Record the decision, including an explicit decision not to expose any. If adopted, agree on tool contracts, discovery and supported browser/runtime behavior, permissions and user confirmation for sensitive actions, and how to verify the integration. Do not silently add a WebMCP surface or assume support is universal.

## Behavior

- Explicit loading, empty, success, and failure states. Preserve useful previous data during transient refresh failures; show a friendly error. Choose polling versus snapshots according to the task, not a universal interval.
- Stable list identity and targeted updates, cleanup/cancellation for async requests, no overlapping polls or disruptive no-change refreshes.
- Treat supplied text as text; do not render untrusted content as executable HTML. Design readable content views with keyboard-operable interactions.

## Module layout

- Separate fetching and rendering. Keep `App.tsx` small: layout plus route wiring only.

```text
client/src/
  App.tsx              # Layout and route wiring
  api.ts               # HTTP boundary and response types
  logging.ts           # Browser diagnostics
  pages/               # Screens; connect route/data state to presentation
  components/          # Shared presentation; e.g. banner, error boundary, per-type views
  hooks/               # Meaningful reusable state/effects: polling, cancellation, recovery
```

- Pages compose a screen and connect route/data state to presentation. Components handle focused interactions/rendering. Hooks own meaningful reusable state/effects, not every trivial fetch or variable.
- API modules own HTTP and error translation; presentation components do not scatter raw fetch calls throughout the UI.
- Keep state near its owner; URL state for navigation, local state for disclosure controls. No global store until a real cross-screen need emerges. Split by responsibility, not arbitrary line limits.

## Accessible HTML for browser automation

- Prefer native buttons, links, inputs, forms, navigation, headings, and landmarks over clickable divs. Explicit labels, unique accessible names, descriptive names for icon-only controls, distinguishable repeated actions.
- Express state with native attributes or appropriate ARIA (`disabled`, `checked`, `selected`, `aria-expanded`, `aria-current`). Native semantics first; ARIA fills gaps.
- Playwright locator preference: `getByRole()` → `getByLabel()` → `getByText()` → `getByTestId()`. Stable test IDs are a fallback, not an excuse to omit accessibility.
- Avoid positional CSS/XPath, coordinates, and screenshot interpretation for ordinary interaction. Ask whether an agent can operate the page from its accessibility tree. Screenshots still help evaluate visual quality.

## Logging

- Browser DevTools Console for sparse, useful diagnostics; friendly UI errors for users. Record safe operation/status/request ID context and rendering failures; preserve server request IDs when available. No private payloads or secrets in browser logs.
- The backend keeps its standard structured logging; do not introduce a parallel server logger for the UI.
- Log failure transitions and recovery rather than every repeated refresh failure. No browser-log upload service by default; add telemetry only for an explicit need and privacy decision.
- Document where to inspect client and server logs and how to correlate them. Demonstrate diagnosing a failure.

## Tests

- Test-driven slices: write and observe the failing test before implementation. Combine focused logic/component tests with Playwright journeys against the actual running service on an isolated data directory and port, using representative fixtures. Verify errors and recovery, not just happy paths.
- Document commands for starting the development server, loading representative data, running checks, and resetting test state.
- Independently exercise the running UI through realistic user paths; verify visible output and important state changes. Test results alone are not product QA; see [quality assurance](../quality-assurance.md) for user walkthroughs.
