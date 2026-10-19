# Mac applications

How we build native macOS apps (SwiftUI/AppKit, Swift Package or Xcode
project). Start simple, but leave a clear path to maturity. These are general
defaults; a project's `ARCHITECTURE/` records where it deviates. For other
platforms see [native-app.md](native-app.md).

## Structure: simple first, with a growth path

- **Composition root.** The SwiftUI `App` (plus an `NSApplicationDelegate`
  if needed) builds one dependencies value — store, platform clients (speech,
  notifications, timers), clock — and hands it to the app's coordinators.
  Tests build their own dependencies with fakes. No DI framework.
- **Layers point inward.** Features (views) → App coordinators (main actor,
  `@Observable`) → pure services (domain logic, planners, state machines) →
  Domain values. Domain and pure services import Foundation only; SwiftUI,
  AppKit, AVFoundation, SwiftData and process APIs stay at named edges.
  Map between layers with small concrete adapters at the outer edge (e.g.
  `DomainPlan → RuntimePlan`), not generic adapter protocols with no users.
- **One owner per piece of state.** A timer or workflow has exactly one state
  machine; views read its snapshot. Do not mirror Domain models into a
  parallel "UI model" layer — views render Domain values plus derived display
  data. Keep presentation-only types only for a stated reason (navigation
  enums, editable drafts of immutable values, formatting, derived outlines).
- **Split coordinators by responsibility, not by layer symmetry.** One app
  model is fine at first; extract when a concrete responsibility appears
  (session coordination, checkpointing, a library of user items, storage
  reporting). Avoid repositories that only wrap one store, TCA, or extra
  packages until a real seam needs them.
- **Observation.** Target macOS 14+ with `@Observable`, `@Environment(Model.self)`
  and `@Bindable`; mark non-UI internals `@ObservationIgnored`. Keep the app
  model and its collaborators `@MainActor`. Use the Swift 6 language mode and
  make any `assumeIsolated`/`@unchecked Sendable` bridge a documented,
  reviewed exception.

## Agent integration: AppleScript and SDEF

During setup or planning, the orchestrator must ask which AppleScript features the app should expose through its scripting definition (SDEF) so agents can integrate with it. Record the agreed objects, properties, commands, and workflows, or an explicit decision to expose none. If adopted, specify stable identifiers, result/error contracts, permissions and confirmation for sensitive actions, and tests using the real app's scripting interface. Route commands through the same application behavior as the UI rather than creating a second state owner. AX-driven QA complements this interface; it does not decide the scripting surface.

## Persistence

- Put storage behind a narrow `@MainActor` protocol; use in-memory and
  failing implementations in tests.
- Route every read and write through one place that logs failures and
  surfaces them in the UI. Never `try?` a write the user would expect to be
  kept. If the store cannot open, run on an in-memory store and say so.
- Version payloads and plan migrations deliberately. A compile-time platform
  alternative (`#if canImport(SwiftData)`) is not a runtime fallback and is
  not legacy compatibility — document which one you have.
- Support a store-location override (`--store-dir <path>` launch argument
  and/or an environment variable) at the composition root so QA can run the
  real app against a temporary store. Default behavior must not change.
- Before changing persisted formats, copy (never move) the real store and
  check its records decode with the new models, using a scratch copy.

## Observability from day one

- `import OSLog`; a few static `Logger(subsystem: Bundle.main.bundleIdentifier ?? "<reverse.dns>", category: …)`
  per area (e.g. planner, runtime, persistence, speech).
- Levels: `debug` for detailed traces (live-streamable, not persisted by
  default), `info` for low-stakes activity, `notice` for state transitions
  and pipeline boundaries (store opened, plan generated, workout started or
  recorded), `error` for recoverable failures, `fault` for broken invariants.
  Retention is OS-controlled; do not promise durations.
- Log context, not objects: operation, stable non-secret ids, counts,
  outcome. Never log health notes, dictated or free text, credentials, or
  whole records. Dynamic values are private by default — mark reviewed
  operational values `privacy: .public`.
- Make invisible side effects observable: a `debug` line per spoken cue,
  notification or sound lets QA assert them without hearing them.
- Diagnose with Console.app or
  `log show --predicate 'subsystem == "<bundle id>"' --last 15m` (use
  `log stream --level debug …` for debug lines). An in-app `OSLogStore`
  viewer only when a support workflow justifies it.

## Accessibility is a feature and the QA seam

- Use native controls with real labels; add `accessibilityLabel`/`Hint`/
  `Value` where visible text is missing or ambiguous; check keyboard and
  VoiceOver behavior.
- Give every interactive control a stable, namespaced, unlocalized
  `accessibilityIdentifier` (`workout.pause`, `settings.voice`), and
  repeated rows an identifier from a persisted record id
  (`history.row.<id>`) — never a regenerated UUID or array index.
- Assert labels separately from identifiers. On macOS, SwiftUI button labels
  appear in the AX description, toggles expose value 0/1, sidebar rows
  navigate by setting `AXSelected` on the row (not by pressing), and sheets
  and alerts are separate windows.

## Product QA ("Playwright for the Mac")

Unit tests are not product QA. Keep an executable journey script that:

1. Builds and ad-hoc signs the app into a **temporary** directory (never
   `~/Applications`) with a **QA bundle id**, so it cannot be confused with,
   or kill, the user's copy, and has its own defaults and window state.
2. Where the app supports it, launches it **backgrounded** (`open -g -n <app> --args --background
   --store-dir <tmp>`; the app sets `.accessory` activation for
   `--background`) so it never steals focus. In the measured macOS 26 setup, SwiftUI created no
   first window for such a launch; verify current behavior and, when needed, open one via the app's own
   `File > New … Window` menu item through AX.
3. Drives it through AX: press by identifier, select sidebar rows, toggle
   checkboxes, and press **menu-bar items** (they work while backgrounded and
   exercise the same commands as keyboard shortcuts, which need focus).
4. **After every interaction re-queries the AX tree** and asserts the
   expected change with a timeout (label flipped, value toggled, text
   appeared, step advanced, time held while paused). Never trust an exit
   code.
5. Captures **window-only** screenshots (`screencapture -x -o -l <CGWindowID>`)
   per step, and a human or vision model actually looks at them.
6. Verifies isolation (hash the real store before and after) and cleans up:
   kill only the QA process, delete the temp install/store and the QA
   bundle's saved state and defaults.

Measured limits to record rather than paper over: synthesized mouse events
(context menus, drag) need a visible, unoccluded window; hidden windows
capture blank; audible output and VoiceOver need a person. Grant the runner
Accessibility and Screen Recording.

Graduate to XCUITest (`XCUIApplication`, identifier queries, page objects,
`XCTAttachment` screenshots) when journeys multiply or CI needs them; a
SwiftPM-only app then needs an Xcode project or UI-test host. Keep the quick
AX script for local smoke runs.

## Ship checklist

1. Composition root with injectable store/platform clients/clock; one owner
   per state machine; adapters at the edges; documented in `ARCHITECTURE/`.
2. Per-area `Logger`s with `notice` milestones and `error` on every caught
   failure; privacy reviewed; no silent `try?` on user data.
3. Stable identifiers and labels on all interactive controls and rows.
4. Store-location override and an executable, isolated AX + screenshot
   journey (a `scripts/qa.sh` entry point with helpers under `scripts/lib/`, or equivalent) with documented permissions.
5. Record evidence and limits: build, tests, live journey results and
   screenshots, signing/notarization status if distributing.
