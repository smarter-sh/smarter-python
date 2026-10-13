# ADR-016: Security

## Status

Accepted

Adapts the platform's [ADR-016: Security](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/016-security.rst).

## Context

The SDK holds api keys that can change production resources, and some of its operations create billable infrastructure. Its repository is public, and its tests use data from real platforms.

## Decision

- The api key is a `SecretStr`, sent only in the `Authorization` header, and masked in logs and `repr()`.
- `deploy()` methods say in their docstrings that they create real infrastructure, and no test calls them.
- Test fixtures from real responses are sanitized: no names, emails, addresses, account numbers, keys or private hostnames.
- The SDK never executes code from a response, and never reads a `.env` file on its own.

## Alternatives Considered

- Leave key handling to the caller.

## Consequences

- **Positive:**
  - Keys don't leak through logs or tracebacks.
- **Negative:**
  - Sanitizing fixtures is manual, and must be reviewed.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-002: Configuration](002-configuration.md)
- [ADR-007: Logging](007-logging.md)
- [ADR-009: Testing](009-testing.md)
