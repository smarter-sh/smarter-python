ADR-012: Docstrings and Documentation
=====================================

Status
------

Superseded in part by :doc:`ADR-023 <023-documentation-site>`, which gives the documentation its own site. The docstring style still applies.

Follows the platform's practice. Note that the platform's `ADR-029: Docstring Style <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/029-docstrings.rst>`__ says Google style, but the platform's code and its ``smarter-docstrings`` skill use reStructuredText; this ADR follows the code.

Context
-------

The SDK's users read docs.smarter.sh, which is built from the platform's repository, and which autodocs the platform's own ``smarter`` package. The SDK's package is also named ``smarter``, so that build can't import the SDK.

Decision
--------

- Docstrings are **reStructuredText** with ``:param:``, ``:returns:`` and ``:raises:`` fields, formatted by pydocstringformatter, exactly as the platform's.
- The SDK's documentation lives **in the platform's repository**, under ``docs/source/smarter-framework/smarter-python*``, so that docs.smarter.sh is one site.
- Its api reference is **generated** from the SDK's docstrings by ``scripts/generate_reference.py``, as Sphinx ``py:`` domain directives that need no import. The generated pages are never edited.
- The SDK's module paths must not collide with the platform's in the shared Sphinx index. That is why its internals are ``smarter.core``, not ``smarter.common``.

Alternatives Considered
-----------------------

- Docs in this repository, on their own site.
- Autodoc in a separate Sphinx build.

Consequences
------------

- **Positive:**

  - One documentation site, one docstring style, and a reference that can't drift from the code.

- **Negative:**

  - Documenting the SDK touches two repositories.

Related ADRs
------------

- :doc:`ADR-000: Introduction <000-intro>`
- :doc:`ADR-001: Scope and Purpose of the SDK <001-scope>`
- :doc:`ADR-013: Type Annotations <013-type-annotations>`
