# ADR Introduction

Architectural Design Records (ADRs) are short documents that capture a single architectural or design decision, its context, and its consequences. Less is more: keep them brief.

These are the ADRs of the Smarter Python SDK. They follow the Smarter platform's own [ADRs](https://github.com/smarter-sh/smarter/tree/main/docs/source/adr): where the SDK applies a platform decision, its ADR says so and links to it, and adapts it to a library that runs in other people's software. The platform's decisions about its own runtime (Django, Docker, Kubernetes, the database, Celery, React, templates, feature flags, internationalization) don't apply to the SDK and are not repeated here.

See: [Michael Nygard's ADRs](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html)

## Guidelines for writing ADRs

- **One decision per ADR.**
- **Be concise.** Focus on clarity and brevity.
- **State the context:** the forces that led to the decision.
- **List the alternatives**, and why they weren't chosen.
- **Explain the decision**, and **describe its consequences**, positive and negative.
- **Use simple language**, for future contributors without today's context.
- **Use the same format** as the others, and **reference related ADRs**.
- **Keep the numbering aligned** with the other SDKs and the smarter cli: a decision that every SDK shares takes this SDK's number. A shared decision made later takes the next number free in every repository, which is why 020 and 021 (language-specific ADRs of the Node.js and Go SDKs) are unused here.

## Index

- [ADR-001: Scope and Purpose of the SDK](001-scope.md)
- [ADR-002: Configuration](002-configuration.md)
- [ADR-003: Writes Go Through the Manifest API](003-writes-through-manifests.md)
- [ADR-004: Pydantic Models, Forward Compatible](004-pydantic-models.md)
- [ADR-005: Mirrored Contracts and Generated SAM Models](005-platform-models.md)
- [ADR-006: Error Handling](006-error-handling.md)
- [ADR-007: Logging](007-logging.md)
- [ADR-008: HTTP Transport, Retries and Timeouts](008-http-transport.md)
- [ADR-009: Testing](009-testing.md)
- [ADR-010: CI/CD](010-ci-cd.md)
- [ADR-011: Dependency Management](011-dependencies.md)
- [ADR-012: Docstrings and Documentation](012-documentation.md)
- [ADR-013: Type Annotations](013-type-annotations.md)
- [ADR-014: Code Quality](014-code-quality.md)
- [ADR-015: Semantic Versioning and API Versions](015-versioning.md)
- [ADR-016: Security](016-security.md)
- [ADR-017: No Response Caching](017-caching.md)
- [ADR-018: A Synchronous Client First](018-synchronous-client.md)
- [ADR-019: Supported Python Versions](019-python-versions.md)
- [ADR-022: A Pinned Copy of the Platform's OpenAPI Document](022-pinned-openapi.md)
