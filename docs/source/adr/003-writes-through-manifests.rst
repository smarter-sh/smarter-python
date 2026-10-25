ADR-003: Writes Go Through the Manifest API
===========================================

Status
------

Accepted

Follows the platform's `ADR-005: Manifests <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/005-manifests.rst>`__, `ADR-006: Rest API <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/006-rest-api.rst>`__ and `ADR-024: Broker Model <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/024-broker-model.rst>`__.

Context
-------

The platform has two ways to change a resource: the brokered manifest api (``/api/v1/cli/apply/``, ``delete/``, ...), which validates a manifest with the kind's Pydantic models and applies its business rules, and the REST views' own POST, PATCH and DELETE handlers. The REST handlers are inconsistent: some create rows from the raw request, set arbitrary attributes, or answer with redirects.

Decision
--------

The SDK creates, changes and deletes resources **only** through the manifest api, exactly as the cli does. It uses the REST api to **read** resources (``list``, ``retrieve``, ``find``), and for **actions** that the manifest api has no verb for, such as evaluating a Guardrail, calling an MCP tool, or searching a vectorstore. Each resource family (``client.guardrails``, ...) binds the manifest operations to its kind.

Alternatives Considered
-----------------------

- Wrap every REST handler, including its writes.
- Offer both, and let the caller choose.

Consequences
------------

- **Positive:**

  - Every write is validated and applied by the platform's broker, as the cli's are.
  - A manifest that works with the cli works with the SDK, and the other way round.

- **Negative:**

  - A write takes a whole manifest, not a single field. Read, change and apply the manifest (``describe()``, ``to_sam()``, ``apply()``).

Related ADRs
------------

- :doc:`ADR-000: Introduction <000-intro>`
- :doc:`ADR-001: Scope and Purpose of the SDK <001-scope>`
- :doc:`ADR-004: Pydantic Models, Forward Compatible <004-pydantic-models>`
- :doc:`ADR-005: Mirrored Contracts and Generated SAM Models <005-platform-models>`
