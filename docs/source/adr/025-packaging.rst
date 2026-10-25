ADR-025: Packaging and Compiled Requirements
============================================

Status
------

Accepted

Supersedes the file layout of :doc:`ADR-011 <011-dependencies>`. Its rule, compatible ranges for the runtime dependencies, is unchanged.

Context
-------

A package's metadata, its build and its requirements should be declared once, in standard files, so that every tool, and every Smarter Project package, reads them the same way. A ``setup.py`` that parses requirements files and rewrites version strings is code that must itself be tested.

Decision
--------

- ``pyproject.toml`` declares the package: its metadata, its runtime dependencies as compatible ranges, and the ``test`` and ``docs`` extras. It is built by hatchling, which reads the version from ``smarter/__version__.py``. Its author is The Smarter Project.
- The requirements files are laid out as the platform's: unpinned ``requirements/in/base.in`` and ``local.in``, global constraints with a reason each in ``requirements/in/constraints.in``, included with ``-c``, and the pinned ``requirements/base.txt`` and ``local.txt``, compiled by pip-compile (``make python-requirements``) and never edited by hand.
- CI installs the package with its extras, not the pinned files, so that it tests what users install.

Alternatives Considered
-----------------------

- Keep ``setup.py``, ``setup.cfg`` and ``MANIFEST.in``.
- Pin the development tools by hand.

Consequences
------------

- **Positive:**

  - One declaration of the package, read by pip, build and hatchling alike.
  - The development environment is reproducible, and updated by one command.

- **Negative:**

  - A runtime dependency's range is written in both ``pyproject.toml`` and ``constraints.in``, and the two must agree.

Related ADRs
------------

- :doc:`ADR-011: Dependency Management <011-dependencies>`
- :doc:`ADR-024: CI and the Release Workflow <024-release-workflow>`
- `Smarter ADR-015: Dependency Management <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/015-dependency-management.rst>`__
