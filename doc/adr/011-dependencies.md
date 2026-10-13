# ADR-011: Dependency Management

## Status

Accepted

Adapts the platform's [ADR-015: Dependency Management](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/015-dependency-management.rst).

## Context

An application, like the platform, pins its dependencies. A library can't: its pins would conflict with its callers'.

## Decision

Runtime dependencies are few (`httpx`, `pydantic`, `pydantic-settings`, `PyYAML`) and declared as compatible ranges in `requirements/base.txt`, which `setup.py` installs. Development tools are pinned in `requirements/local.txt`. Dependabot and Mergify keep both current, as on the platform.

## Alternatives Considered

- Pin runtime dependencies.
- Unbounded ranges.

## Consequences

- **Positive:**
  - The SDK installs beside any application's own pins.
- **Negative:**
  - The ranges must be tested: CI's matrix runs the latest versions within them.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-010: CI/CD](010-ci-cd.md)
