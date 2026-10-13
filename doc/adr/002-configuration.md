# ADR-002: Configuration

## Status

Accepted

Adapts the platform's [ADR-004: 12-Factor App](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/004-12-factor.rst) and [ADR-007: Settings](https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/007-settings.rst).

## Context

A client needs an api key and the url of a platform. Programmers configure libraries in code, operators configure them with environment variables (12-factor), and Smarter developers already have both in the smarter cli's `~/.smarter/config.yaml`.

## Decision

One Pydantic settings model, `smarter.core.conf.SmarterSettings`, is the only code that reads the environment (`SMARTER_*` variables), as the platform's `Settings` singleton is. `resolve_client_config()` takes each value from the first of: the client's arguments, the environment, the cli's configuration file, and the defaults (`prod` on `platform.smarter.sh`). Without a base url, the url is derived from the environment exactly as the cli derives it. The api key is a `SecretStr`.

The SDK never reads a `.env` file itself: an application decides how its environment is loaded.

## Alternatives Considered

- Arguments only, as a minimal library would do.
- Read `.env` automatically. A library that reads its caller's working directory surprises its caller.
- A configuration file of the SDK's own.

## Consequences

- **Positive:**
  - Developers who use the cli need no setup.
  - Deployments configure the SDK with environment variables alone.
  - Every value is validated in one place.
- **Negative:**
  - The lookup order must be documented and tested, because a value can come from four places.

## Related ADRs

- [ADR-000: Introduction](000-intro.md)
- [ADR-001: Scope and Purpose of the SDK](001-scope.md)
- [ADR-016: Security](016-security.md)
