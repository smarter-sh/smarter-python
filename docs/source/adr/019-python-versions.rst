ADR-019: Supported Python Versions
==================================

Status
------

Accepted

Context
-------

The platform runs on the newest Python. The SDK runs in its callers' environments, which are often older.

Decision
--------

The SDK supports every Python version that is not end-of-life: 3.10 and later
as of October 2026. CI tests each one (ADR-010). Code uses ``Optional[...]`` and ``Union[...]``, as the platform does, rather than syntax that a newer minimum would allow.

Alternatives Considered
-----------------------

- Only the platform's Python version.

Consequences
------------

- **Positive:**

  - The SDK installs in most current environments.

- **Negative:**

  - The minimum rises as versions reach end-of-life, which is a breaking change for callers on them.

Related ADRs
------------

- :doc:`ADR-000: Introduction <000-intro>`
- :doc:`ADR-010: CI/CD <010-ci-cd>`
- :doc:`ADR-013: Type Annotations <013-type-annotations>`
