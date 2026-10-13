# ADR-005: Mirrored Contracts and Generated SAM Models

## Status

Accepted

## Context

The platform's Pydantic models are the source of truth of its api: the SAM models of every manifest kind, and the published contracts (the Smarter Chat api, the Smarter Journal, the Django-React integration). The SDK can't import them: the platform's package is also named `smarter`, and its SAM models depend on Django.

## Decision

- **SAM models** are generated from the JSON Schema that the platform publishes for each kind (`/api/v1/cli/json-schema/<Kind>/`), by `scripts/generate_sam_models.py` (datamodel-code-generator) into `smarter/models/sam/`. The schemas and example manifests are saved in `tests/data/sam/`, and a test parses every kind's example with its model. Generated code is never edited by hand.
- **Contracts** are mirrored by hand in `smarter/models/chat.py` and `journal.py`, and copied in `react.py` (which is pure Pydantic). `scripts/sync-contracts.sh` copies the platform's committed JSON Schemas and examples into `tests/data/contracts/`, and a test fails when the platform declares a field that the mirror doesn't, or when an example doesn't parse.
- The SDK reads **only version 2** of the chat contract, and asks for it in every request (`X-Smarter-Capabilities: chat-contract-v2`).

## Alternatives Considered

- Import the platform's models. Impossible, as above.
- Hand-write the SAM models. 25 kinds, which drift as soon as they are written.
- Generate the contracts too. Hand-mirroring keeps their docstrings, helpers (`.text`) and forward-compatible types (ADR-004).

## Consequences

- **Positive:**
  - Callers get the platform's own models.
  - Drift is caught by tests, not by users.
- **Negative:**
  - Refreshing is a manual step (`make sam-models`, `make contracts`) that someone must run when the platform changes.
  - Generated models check structure, not the platform's business rules: `manifests.validate()` does.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-001: Scope and Purpose of the SDK](001-scope.md)
- [ADR-004: Pydantic Models, Forward Compatible](004-pydantic-models.md)
- [ADR-009: Testing](009-testing.md)
