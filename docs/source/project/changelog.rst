Changelog
=========

Releases are made by `semantic-release <https://semantic-release.gitbook.io/>`__ from the
project's conventional commit messages, which also write
`CHANGELOG.md <https://github.com/smarter-sh/smarter-python/blob/main/CHANGELOG.md>`__. Each
release's notes are on its `GitHub release page <https://github.com/smarter-sh/smarter-python/releases>`__.

Versions follow `semantic versioning <https://semver.org/>`__:

- a **patch** release (0.5.3) fixes bugs,
- a **minor** release (0.6.0) adds features, and keeps working code working,
- a **major** release (1.0.0) can break code.

The SDK is versioned independently of the platform: it targets the platform's ``smarter.sh/v1``
api, and ``client.version()`` reports the platform's own version. See
:doc:`../adr/015-versioning`.
