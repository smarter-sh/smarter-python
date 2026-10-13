# ADR-006: Error Handling

## Status

Accepted

Adapts the platform's [ADR-012: Error Handling](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/012-error-handling.rst).

## Context

Callers need to tell a missing resource from a bad manifest, an expired key, an unreachable server, or a platform bug, and the platform returns errors in several shapes: the journal's `error` object, an `error` string, Django REST Framework's `detail`, and Django's html error page.

## Decision

Every exception that the SDK raises subclasses `smarter.core.exceptions.SmarterError`, as the platform's subclass `smarter.common.exceptions` (ADR-012). An http error raises the subclass of `APIStatusError` for its status (`NotFoundError` for 404, ...), which carries the status, a readable message from whichever shape the platform used, the body, and the journal's error (with the platform's `errorClass`) when there is one. `NotFoundError` is also a `ResourceNotFoundError`, which `find()` raises, so one `except` clause handles both.

## Alternatives Considered

- Let `httpx` exceptions propagate.
- One exception class with a status attribute.

## Consequences

- **Positive:**
  - Callers catch exactly what they can handle.
  - Platform errors keep their server-side class name.
- **Negative:**
  - The mapping of the platform's error shapes must follow the platform.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-004: Pydantic Models, Forward Compatible](004-pydantic-models.md)
- [ADR-008: HTTP Transport, Retries and Timeouts](008-http-transport.md)
