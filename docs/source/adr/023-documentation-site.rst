ADR-023: A Documentation Site of Its Own
========================================

Status
------

Accepted

Supersedes the documentation location of :doc:`ADR-012 <012-documentation>`. Its docstring style still applies.

Context
-------

The SDK is released on its own schedule (:doc:`ADR-015 <015-versioning>`), and its users need documentation of the version they install. The platform's Sphinx build autodocs the platform's own ``smarter`` package, so it can't import the SDK, whose import name is also ``smarter``: its api reference had to be generated as directives that need no import, and every change to the documentation touched two repositories.

Decision
--------

The SDK's documentation lives in this repository, in ``docs/source/``, and is published to https://docs.smarter-python.smarter.sh/.

- It is built by Sphinx with the Read the Docs theme, as the platform's documentation is. ``make sphinx-build`` treats every warning as an error, and CI builds it on every push and pull request.
- The api reference is autodoc of the SDK itself, from its reStructuredText docstrings.
- The site is static: a private S3 bucket behind CloudFront, with a certificate and DNS records in the ``smarter.sh`` zone, all declared in ``terraform/docs/``. ``make sphinx-publish`` uploads a build.
- Every page's footer says that the SDK is part of The Smarter Project, and links to https://smarter.sh.
- The platform's documentation keeps a short page about the SDK that links here.

Alternatives Considered
-----------------------

- Keep the documentation in the platform's repository, with a generated api reference.
- Read the Docs hosting, which adds its own advertising and version menu to every page.
- GitHub Pages, which would host the site outside the Terraform that holds the other Smarter Project sites.

Consequences
------------

- **Positive:**

  - A change to the SDK and its documentation is one pull request, reviewed and built together.
  - The api reference is ordinary autodoc, and can't drift from the code.
  - The site is the same shape as the other Smarter Project packages' sites.

- **Negative:**

  - One more site to publish, and its AWS resources to keep.
  - Links between the SDK's and the platform's documentation are absolute urls, which Sphinx doesn't check.

Related ADRs
------------

- :doc:`ADR-012: Docstrings and Documentation <012-documentation>`
- :doc:`ADR-024: CI and the Release Workflow <024-release-workflow>`
- `Smarter ADR-029: Docstring Style <https://github.com/smarter-sh/smarter/blob/main/docs/source/adr/029-docstrings.rst>`__
