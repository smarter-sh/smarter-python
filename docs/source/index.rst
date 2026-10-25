Smarter Python SDK
==================

.. image:: https://img.shields.io/badge/a%20project%20of-The%20Smarter%20Project-2F6FEB
   :target: https://smarter.sh
   :alt: A project of The Smarter Project

.. image:: https://github.com/smarter-sh/smarter-python/actions/workflows/ci.yml/badge.svg?branch=main
   :target: https://github.com/smarter-sh/smarter-python/actions/workflows/ci.yml
   :alt: CI

.. image:: https://codecov.io/gh/smarter-sh/smarter-python/graph/badge.svg
   :target: https://codecov.io/gh/smarter-sh/smarter-python
   :alt: Coverage

.. image:: https://img.shields.io/github/v/release/smarter-sh/smarter-python?label=release
   :target: https://github.com/smarter-sh/smarter-python/releases
   :alt: Latest release

.. image:: https://img.shields.io/pypi/v/smarter-api?logo=pypi&label=PyPI
   :target: https://pypi.org/project/smarter-api/
   :alt: PyPI

.. image:: https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white
   :alt: Python 3.10+

.. image:: https://img.shields.io/badge/License-AGPL_v3-blue.svg
   :target: https://github.com/smarter-sh/smarter-python/blob/main/LICENSE.txt
   :alt: GNU AGPL v3 License

|

The Smarter Python SDK is the official Python library of the `Smarter API <https://docs.smarter.sh/en/latest/smarter-framework/smarter-api.html>`__. It is
to Smarter what the ``openai`` package is to the OpenAI API: one ``pip install`` gives your Python
software typed, complete access to your own Smarter platform, whether it runs on your laptop or on
`Kubernetes <https://docs.smarter.sh/en/latest/smarter-framework/smarter-on-kubernetes.html>`__.

Use it to build custom software that is tightly integrated with your Smarter resources, without
customizing or forking the Smarter platform: a web application that chats with your
`LLMClients <https://docs.smarter.sh/en/latest/smarter-resources/smarter-llmclient.html>`__, a CI/CD job that applies your
`manifests <https://docs.smarter.sh/en/latest/smarter-framework/smarter-manifests.html>`__, a data pipeline that loads documents into a
`Vectorstore <https://docs.smarter.sh/en/latest/smarter-resources/smarter-vectorstore.html>`__, a service that calls the tools of your
`MCP servers <https://docs.smarter.sh/en/latest/smarter-resources/smarter-mcpclient.html>`__, or a test suite for your prompts.

.. code-block:: console

   $ pip install smarter-api

.. code-block:: python

   from smarter import Smarter

   client = Smarter()  # SMARTER_API_KEY, or the smarter cli's ~/.smarter/config.yaml

   llmclient = client.llm_clients.find("customer_support")
   response = client.llm_clients.prompt(llmclient.id, "Where is my order #1234?")
   print(response.text)

The package is ``smarter-api`` on `PyPI <https://pypi.org/project/smarter-api/>`__, and its import
name is ``smarter``. Its source is
`github.com/smarter-sh/smarter-python <https://github.com/smarter-sh/smarter-python>`__.

It is part of `The Smarter Project <https://smarter.sh>`__, and the reference client of the api of
`Smarter <https://github.com/smarter-sh/smarter>`__, an open-source platform for building and
running AI applications with Django. The platform's own documentation is on
`docs.smarter.sh <https://docs.smarter.sh/>`__.


The SDK or the CLI?
-------------------

The SDK and the `Smarter CLI <https://docs.smarter.sh/en/latest/smarter-framework/smarter-cli.html>`__ manage the same resources, through the same API.
The difference is how you use them.

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Smarter Python SDK
     - Smarter CLI
   * - A Python library that you **import** into your own software.
     - A program that you **install** on your computer.
   * - ``client.manifests.apply("guardrail.yaml")``
     - ``smarter apply -f guardrail.yaml``
   * - Returns typed Pydantic models, and raises typed exceptions.
     - Prints JSON or YAML in a terminal window.
   * - For applications, services, notebooks, tests and automation.
     - For people at a keyboard, and shell scripts.

The SDK reads the CLI's configuration file, so a developer who has run ``smarter configure`` needs
no other setup.


What It Covers
--------------

- **Every resource kind**, through the same brokered `manifest API <https://docs.smarter.sh/en/latest/smarter-framework/smarter-api/cli.html>`__ that the
  CLI uses: ``apply``, ``validate``, ``get``, ``describe``, ``delete``, ``deploy``, ``undeploy`` and
  ``logs``.
- **Prompts and conversations**: prompt an LLMClient, hold a multi-turn chat that keeps its session,
  and stream a prompt's progress as it runs, exactly as `Smarter Chat <https://docs.smarter.sh/en/latest/smarter-framework/smarter-chat.html>`__ does.
- **Resource actions**: evaluate a Guardrail, call an MCP server's tools, add documents to and
  search a Vectorstore, plan and deploy an LLMHost, discover open-weight models, read the chat
  history and the `Smarter Journal <https://docs.smarter.sh/en/latest/smarter-framework/smarter-api/smarter-journal.html>`__, and call an LLM provider
  through a Proxy.
- **The platform's own Pydantic models**: a typed model of every manifest kind, the
  `Smarter Chat API contract <https://docs.smarter.sh/en/latest/smarter-framework/smarter-chat/api-contract.html>`__, the Smarter Journal contract and the
  `Django-React integration <https://docs.smarter.sh/en/latest/smarter-framework/developer-reference/react-integration.html>`__ contract.


Where to Start
--------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - If you want to...
     - Read
   * - Connect to your platform: api keys, urls, environments, timeouts
     - :doc:`Configuration <guide/configuration>`
   * - Create, change and delete resources from Python
     - :doc:`Manifests <guide/manifests>`
   * - Prompt an LLMClient, chat with it, or stream its progress
     - :doc:`Prompts and Chat <guide/chat>`
   * - Use Guardrails, MCP clients, Vectorstores, LLMHosts and the other resources
     - :doc:`Resources <guide/resources>`
   * - Build manifests in code, or read the API's contracts as typed models
     - :doc:`Models <guide/models>`
   * - Handle errors, retries, timeouts and logging
     - :doc:`Errors and Reliability <guide/errors>`
   * - Install the SDK, and send your first prompt
     - :doc:`Installation <installation>` and :doc:`Quickstart <quickstart>`
   * - Contribute to the SDK
     - :doc:`Contributing <project/contributing>`
   * - Look up a class or method
     - :doc:`API Reference <reference>`


.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   guide/configuration
   guide/manifests
   guide/chat
   guide/resources
   guide/models
   guide/errors

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference

.. toctree::
   :maxdepth: 1
   :caption: Project

   project/changelog
   project/contributing
   project/license
   adr

Indices
-------

- :ref:`genindex`
- :ref:`modindex`
- :ref:`search`
