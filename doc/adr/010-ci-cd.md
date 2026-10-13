# ADR-010: CI/CD

## Status

Accepted

Follows the platform's [ADR-014: CI/CD](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/014-ci-cd.rst).

## Context

Every change should be tested, and every release built the same way.

## Decision

GitHub Actions only, as on the platform. `test.yml` runs the unit tests on Python 3.10 to 3.14 for every push and pull request, enforces 90% coverage, and uploads coverage to Codecov. `build.yml` builds the sdist and wheel and checks them with twine. Releases are versioned by semantic-release (ADR-015). Publishing to PyPI is done by hand (`make publish-prod`).

## Alternatives Considered

- Other CI services.

## Consequences

- **Positive:**
  - Consistent with the platform's workflows.
- **Negative:**
  - Publishing is a manual step.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-009: Testing](009-testing.md)
- [ADR-015: Semantic Versioning and API Versions](015-versioning.md)
