Installation
============

.. code-block:: console

    $ pip install smarter-api

The package is ``smarter-api`` on `PyPI <https://pypi.org/project/smarter-api/>`__, and its import
name is ``smarter``. It needs Python 3.10 or newer, and depends on httpx, Pydantic,
pydantic-settings and PyYAML. It ships a ``py.typed`` marker, so type checkers read its
annotations.

You also need a Smarter platform to connect to, and an api key of one of its users. To run a
platform on your own computer, see the platform's
`Quick Start Guide <https://docs.smarter.sh/en/latest/smarter-platform/installation/quick-start.html>`__.

Prereleases
-----------

Prereleases from the ``alpha`` and ``beta`` branches, e.g. ``0.6.0a1``, are published to
`TestPyPI <https://test.pypi.org/project/smarter-api/>`__ only. Install the dependencies from PyPI
first, then only the SDK itself from TestPyPI, where anyone can publish a package named like one of
its dependencies:

.. code-block:: console

    $ pip install httpx pydantic pydantic-settings PyYAML email-validator
    $ pip install --no-deps --index-url https://test.pypi.org/simple/ "smarter-api==0.6.0a1"

Next, :doc:`point the SDK at your platform <quickstart>`.
