ADR-001: Scope and Purpose of the SDK
=====================================

Status
------

Accepted

Context
-------

The Smarter platform is managed through its REST api. The smarter cli (Go) serves people at a terminal, and Smarter Chat (React) serves web pages, but Python programmers who want to build their own software on a Smarter installation had only a prototype library that covered one deprecated endpoint. Without a complete SDK, the only way to integrate deeply with Smarter was to customize or fork the platform.

Decision
--------

smarter-python is the platform's official, complete Python SDK, published to PyPI as ``smarter-api`` with the import name ``smarter``. It is to Smarter what the ``openai`` package is to the OpenAI api:

- it covers **all** of the platform's public api: every resource kind through the manifest api, the chat and prompt apis, and every resource's REST reads and actions,
- it exposes the platform's own Pydantic models: the SAM models of every kind, and the api contracts (ADR-005),
- it serves programmers who *import* it, while the cli serves people who *run* it. Both use the same api, and the SDK reads the cli's configuration file (ADR-002).

The platform is never imported. Everything goes through its http api, so the SDK works against a platform on a laptop or on Kubernetes, of any version that serves ``smarter.sh/v1``.

Alternatives Considered
-----------------------

- Keep the prototype's narrow, chatbot-only scope.
- Generate a client from the platform's OpenAPI (Swagger) document. The document covers the REST views but not the manifest api's broker semantics, the chat contract, or streaming, and generated clients read poorly.
- Make the platform importable as a library. It depends on Django, a database and Redis.

Consequences
------------

- **Positive:**

  - Python software can integrate with Smarter without forking it.
  - One library is the reference client of the platform's api, so it finds the api's inconsistencies and bugs.

- **Negative:**

  - The SDK must track the platform's api as it changes (ADR-005, ADR-015).
  - The import name ``smarter`` is also the platform's package name (ADR-012).

Related ADRs
------------

- :doc:`ADR-000: Introduction <000-intro>`
- :doc:`ADR-002: Configuration <002-configuration>`
- :doc:`ADR-003: Writes Go Through the Manifest API <003-writes-through-manifests>`
- :doc:`ADR-005: Mirrored Contracts and Generated SAM Models <005-platform-models>`
