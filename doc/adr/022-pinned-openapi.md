# ADR-022: A Pinned Copy of the Platform's OpenAPI Document

## Status

Accepted

The Node.js and Go SDKs and the smarter cli share this decision, under the same number.

## Context

The platform publishes its api as an OpenAPI document, generated from its Pydantic models and committed as `smarter/smarter/apps/api/v1/contract/openapi.json` (the platform's `smarter-api-contract` skill). It covers the cli api (`/api/v1/cli/`), the chat api, and every family of REST routes, with their request and response schemas.

The SDK's unit tests replay recorded responses from a mock transport (ADR-009). A mock answers whatever path it is asked, so it can't tell when the SDK calls a route that the platform renamed or removed, or when a recorded fixture no longer matches what the platform sends. The smarter cli shipped two broken commands for that reason (`example_manifest/` and `chat/`, renamed by the platform), with every unit test passing.

## Decision

The SDK keeps a **copy** of the platform's `openapi.json`, pinned to a platform version, in `tests/data/contracts/openapi.json`, and tests against it:

- `scripts/sync-contracts.sh` (`make contracts`, or `make contracts SMARTER_REF=<tag>`) copies it from a checkout of the platform, at its working tree or at a git ref, with the other contracts (ADR-005). The copy is committed, and is never edited by hand.
- `tests/test_contracts.py` checks that every request the SDK sends matches an operation of the document (method and path template), and that the SDK calls every operation, apart from a named list of operations it deliberately doesn't call, each with its reason.
- It checks that every recorded fixture in `tests/data/` that the tests replay is valid under the document's schema for that operation's 200 response.
- Refreshing the copy is part of the monthly maintenance; a failing contract test after a refresh is how the SDK learns what changed.

## Alternatives Considered

- Fetch the document from a running platform during the tests. Tests would need the network and a platform, and would change under the SDK without a commit.
- Read it from `../smarter` during the tests. CI has no platform checkout, and the result would depend on whatever branch is checked out.
- Generate the client from the document. See ADR-001.
- Rely on live tests alone. They are opt-in, and can't cover operations that are unsafe to call (deploy).

## Consequences

- **Positive:**
  - Drift between the SDK and the platform fails a unit test, in CI, rather than reaching users.
  - The diff of the copy, at each refresh, is a precise list of the api's changes.
  - The four Smarter clients (three SDKs and the cli) check themselves against the same document.
- **Negative:**
  - The copy is only as current as its last refresh; a platform change is caught at the next `make contracts`, not when it lands.
  - The named list of uncalled operations must be kept honest.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-005: Mirrored Contracts and Generated SAM Models](005-platform-models.md)
- [ADR-009: Testing](009-testing.md)
