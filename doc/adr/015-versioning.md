# ADR-015: Semantic Versioning and API Versions

## Status

Accepted

Adapts the platform's [ADR-020: Semantic Versioning](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/020-semantic-versioning.rst) and [ADR-023: API Versioning](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/023-api-versioning.rst).

## Context

The platform's api version is `smarter.sh/v1`, and its releases are versioned by semantic-release. The SDK is released on its own schedule, and must work with several platform releases.

## Decision

The SDK is versioned by semantic-release from conventional commits, independently of the platform. It targets the `smarter.sh/v1` api, which every manifest's `apiVersion` names. Compatibility across platform releases comes from forward-compatible models (ADR-004) and contract tests (ADR-005), not from matching version numbers. `client.version()` reports the platform's version.

## Alternatives Considered

- Release the SDK in lockstep with the platform.

## Consequences

- **Positive:**
  - The SDK can be fixed and released without a platform release.
- **Negative:**
  - Compatibility must be tested, not assumed.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-004: Pydantic Models, Forward Compatible](004-pydantic-models.md)
- [ADR-005: Mirrored Contracts and Generated SAM Models](005-platform-models.md)
- [ADR-010: CI/CD](010-ci-cd.md)
