# Backend service

Recommendations, not rules. If a stack, layer, or convention below does not fit the project, propose a better alternative with its rationale. Re-examine the specific technology recommendations when the date is later than January 1, 2027; prefer newer or better-supported alternatives where they exist. Covers standalone local HTTP/JSON services as well as background and distributed services; identify service boundaries, message contracts, data ownership, retries, and idempotency in `ARCHITECTURE/` when distribution is involved.

## Preferred stack

- TypeScript on a supported Node.js version, Fastify, and SQLite for embedded persistence. Start with SQLite in most situations; move to Postgres or similar when production needs demand it. State the minimum Node version required by the chosen APIs rather than freezing a project-specific version.
- Prefer a modular monolith over separate processes for each business component. Distinguish logical service boundaries from deployment boundaries.

## Layering

- HTTP/API → application/business services → persistence repositories → datastore. Business logic lives in the service layer, not a separate mandatory parallel layer.
- API handlers validate and map requests/responses. Services coordinate use cases and failure behavior. Repositories encapsulate queries. The datastore owns connections, schema, and transactions.
- Compose dependencies at startup. Small functions/modules and explicit dependencies suffice; no mandatory DI framework, interface per class, or empty layers.
- Keep project-specific service names out of this skill; domain services are distinct from persistence repositories.

## Contracts and data

- Specify request/response contracts, validation, errors, identity, omission versus empty-value semantics, and update/idempotency behavior before implementation. Define what survives restart.
- Pick one source of truth; treat generated files as derived data. Define failure and retry behavior across database/filesystem boundaries rather than implying atomicity. Validate before side effects; guard paths and never execute supplied content implicitly.
- For local tools, bind loopback by default; local binding does not replace evaluating auth, origin, and permission needs.

## Configuration and operation

- Resolve configuration once and reuse it: process environment > project `.env` > application-data settings file > defaults. Resolve the data directory before reading its settings. Keep secrets server-side.
- Reuse the root `scripts/` convention: terse README, start/stop scripts, seed scripts, environment overrides, and ownership-aware process management. Never stop or reuse an unrelated listener.
- Isolate test/demo data directories and ports. Seed tooling verifies its target and refuses production before any filesystem or network writes. Guard tests use a simulated data directory, not the real production location; consider symlinks and case aliases.

## Logging

- Use Fastify's Pino integration: structured JSON, request IDs, and consistent operation/outcome/status/duration context. Correlate service and persistence failures without logging duplicate noise.
- For standalone local services, bounded rotating files under the configured application home plus useful process output. Deployment platforms may instead collect stdout; adapt rather than forcing local file rotation everywhere.
- Document levels, locations, retention, and filtering. Test redaction and failure diagnostics. Do not log bodies, arbitrary metadata, credentials, sensitive URLs, or content-bearing error messages; sanitize error details and stacks.

## Tests and QA

- Test-first vertical slices with observed failing/passing behavior. Business behavior must be testable without a live external system; add pure logic tests plus real HTTP/SQLite/filesystem integration in disposable homes. Use controlled fixtures or local dependencies where possible; do not mistake mocks for end-to-end evidence.
- For QA, operate the running service through its real API/entry point and verify observable behavior, authorization, persistence, restart behavior, and relevant error cases. Tests alone are not product QA; see [quality assurance](../quality-assurance.md) for user walkthroughs.
- Provide reproducible startup/input/inspection/stop commands. User-requested review gates remain optional unless a task requires one.
- Document local startup, health/status inspection, queue/job inspection, and test-data setup. Independently verify asynchronous completion, retries, and failure reporting where they apply.
