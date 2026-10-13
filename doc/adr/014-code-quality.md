# ADR-014: Code Quality

## Status

Accepted

Follows the platform's [ADR-028: Code Quality](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/028-code-quality.rst).

## Context

Consistent code is easier to review, and the SDK is developed beside the platform.

## Decision

`.pre-commit-config.yaml` is the standard, with the platform's hooks (black, isort, autoflake, flake8, bandit, pyupgrade, pydocstringformatter, codespell, prettier, commitlint), minus its React hooks. Rules aren't disabled indiscriminately.

## Alternatives Considered

- A separate style for the SDK.

## Consequences

- **Positive:**
  - The SDK and the platform read alike.
- **Negative:**
  - Hook versions must be kept in step with the platform's.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-012: Docstrings and Documentation](012-documentation.md)
