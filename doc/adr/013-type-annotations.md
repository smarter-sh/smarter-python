# ADR-013: Type Annotations

## Status

Accepted

Follows the platform's [ADR-027: Python Annotations](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/027-annotations.rst).

## Context

The SDK's annotations are read by its callers' type checkers and editors, not only by its own developers.

## Decision

All code is annotated, and the package ships `py.typed`. `Any` is used only where a value really can be anything (e.g. a type form). Repeated constructions are the `Smarter...Type` aliases of `smarter.core.typing`, which mirror the platform's `smarter.lib.typing`. Resource modules use `from __future__ import annotations`, because their `list()` methods shadow the builtin in class-level annotations.

## Alternatives Considered

- Partial annotations.

## Consequences

- **Positive:**
  - Callers get completion and type checking for every call and response.
- **Negative:**
  - Annotations are part of the public api, and change with it.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-004: Pydantic Models, Forward Compatible](004-pydantic-models.md)
