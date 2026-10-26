# The Smarter Python SDK

[![A project of The Smarter Project](https://img.shields.io/badge/a%20project%20of-The%20Smarter%20Project-2F6FEB)](https://smarter.sh)
[![Release](https://github.com/smarter-sh/smarter-python/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/smarter-sh/smarter-python/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/smarter-sh/smarter-python/graph/badge.svg)](https://codecov.io/gh/smarter-sh/smarter-python)
[![Latest Release](https://img.shields.io/github/v/release/smarter-sh/smarter-python?label=release)](https://github.com/smarter-sh/smarter-python/releases)
[![PyPI](https://img.shields.io/pypi/v/smarter-api?logo=pypi&label=PyPI)](https://pypi.org/project/smarter-api/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/smarter-api?label=downloads&logo=pypi&logoColor=white)](https://pypi.org/project/smarter-api/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE.txt)
[![Docs](https://img.shields.io/badge/docs-docs.smarter--python.smarter.sh-blue?logo=readthedocs)](https://docs.smarter-python.smarter.sh/)

`smarter-api` is the official Python SDK of the
[Smarter platform](https://github.com/smarter-sh/smarter). It is to Smarter what
the `openai` package is to the OpenAI api: one `pip install` gives your Python
software typed, complete access to your own Smarter installation, whether it
runs on your laptop or on Kubernetes.

Use it to build custom software that is tightly integrated with your Smarter
resources and functionality, without customizing or forking the Smarter
backend: a web application that chats with your LLMClients, a CI job that
applies your manifests, a data pipeline that loads documents into a
vectorstore, or a service that calls your MCP servers' tools.

```python
from smarter import Smarter

client = Smarter()  # SMARTER_API_KEY, or the smarter cli's ~/.smarter/config.yaml

llmclient = client.llm_clients.find("customer_support")
response = client.llm_clients.prompt(llmclient.id, "Where is my order #1234?")
print(response.text)
```

**Documentation: <https://docs.smarter-python.smarter.sh/>**

smarter-python is part of [The Smarter Project](https://smarter.sh).

## Smarter Python SDK or Smarter CLI?

Both manage the same resources through the same api. The difference is how
you use them:

| [smarter-python](https://github.com/smarter-sh/smarter-python) (this package) | [smarter-cli](https://github.com/smarter-sh/smarter-cli) |
| ----------------------------------------------------------------------------- | -------------------------------------------------------- |
| A Python library that you **import** into your own software.                  | A program that you **install** on your computer.         |
| `client.manifests.apply("guardrail.yaml")`                                    | `smarter apply -f guardrail.yaml`                        |
| Returns typed Pydantic models, and raises typed exceptions.                   | Prints JSON or YAML in a terminal window.                |
| For applications, services, notebooks, tests and automation.                  | For people at a keyboard, and shell scripts.             |

The SDK reads the cli's configuration file, so if you have run
`smarter configure`, the SDK needs no other setup.

## At a Glance

- **Every resource kind**, through the same manifest api as the cli:
  `apply`, `validate`, `get`, `describe`, `delete`, `deploy`, `undeploy` and
  `logs`, for LLMClients, Plugins, Guardrails, MCPClients, Vectorstores,
  LLMHosts, Secrets, Custom Domains, Accounts, Users, and every other kind.
- **Prompts and conversations**: prompt an LLMClient, hold a multi-turn chat
  that keeps its session, and stream a prompt's progress (its LLM requests,
  tool calls and MCP calls) as it runs.
- **Resource actions**: evaluate a Guardrail, call an MCP server's tools, add
  documents to and search a vectorstore, plan and deploy an LLMHost, discover
  open-weight models, and call an LLM provider through a Proxy.
- **The platform's own Pydantic models**: a typed model of every
  [SAM manifest](https://docs.smarter.sh/en/latest/smarter-framework/smarter-manifests.html)
  kind (e.g. `SAMLLMClient`), the Smarter Chat api contract (e.g.
  `PromptChatApiConfig`), the Smarter Journal contract, and the Django-React
  integration contract, kept in step with the platform by tests.
- **Production behavior**: retries with backoff, timeouts, typed exceptions,
  logging that never prints your api key, and a `py.typed` package for your
  type checker.

## Quickstart

```console
pip install smarter-api
```

Point the SDK at your platform with environment variables, or pass them as
arguments to `Smarter(...)`:

```console
export SMARTER_API_KEY="your 64-character Smarter api key"
export SMARTER_BASE_URL="https://platform.example.com"   # or http://localhost:9357
```

### Manifests

```python
from smarter import Smarter

client = Smarter()

client.manifests.apply("pii-redactor.yaml")                    # create or update
manifest = client.guardrails.describe("pii_redactor")          # read it back
guardrail = manifest.to_sam()                                  # as a typed SAMGuardrail
print(guardrail.spec.config.action)
client.guardrails.delete("pii_redactor")
```

### Chat

```python
chat = client.llm_clients.chat(llmclient.id)
print(chat.send("What is 2 to the 10th power?").text)
print(chat.send("And divided by 4?").text)

with chat.stream("Now take its square root.") as stream:
    for event in stream:
        print("...", event.message)     # e.g. "Calling tool calculator"
    print(stream.response.text)
```

`client.llm_clients.config(llmclient.id)` returns the chat configuration that a
session starts with. It has what a chat needs, and only the counts of the
LLMClient's plugins and extensions. Pass `verbose=True` for the complete
configuration, with their lists and the session's tool calls.

### Errors

```python
from smarter import NotFoundError, SmarterError

try:
    client.manifests.describe("LLMClient", "no_such_client")
except NotFoundError as e:
    print(e.status_code, e.message, e.error_class)
except SmarterError as e:
    print("something else went wrong:", e)
```

## Documentation

The SDK's documentation is at <https://docs.smarter-python.smarter.sh/>: the
user guide, the api reference generated from its docstrings, and its
architecture decision records. The platform's own documentation is at
[docs.smarter.sh](https://docs.smarter.sh/).

## Requirements

Python 3.10 or later, and a Smarter platform to connect to. See the
[Quick Start Guide](https://docs.smarter.sh/en/latest/smarter-platform/installation/quick-start.html)
to run one on your laptop.

## Development

```console
make                # list every command
make init           # create venv/ from requirements/local.txt, install the package and the git hooks
make test           # the unit tests, which never reach a platform
make coverage       # the unit tests, with a coverage report
SMARTER_BASE_URL=http://localhost:9357 SMARTER_API_KEY=... make test-live
make lint           # run the pre-commit hooks on every file
make sphinx-build   # build the Sphinx docs into docs/build/html
make sphinx-publish # publish them to docs.smarter-python.smarter.sh (releases do it themselves)
make build          # build the sdist and wheel, and check them
make python-requirements  # recompile the pinned requirements/*.txt
```

CI runs the hooks, the unit tests on every supported Python version, the docs
build and a package build, on every pull request, and on every push to `main`,
`alpha` and `beta` as the first step of the Release workflow. Coverage is
reported to [Codecov](https://codecov.io/gh/smarter-sh/smarter-python). When CI
passes, the Release workflow releases with semantic-release, from the
conventional commit messages, and publishes to PyPI from `main` (or to TestPyPI
from `alpha` and `beta`). Once PyPI has a release from `main`, the same
workflow publishes its documentation to docs.smarter-python.smarter.sh.
`make release-dry-run` shows the next version.

The agent skills in [skills/](./skills/) describe how this repository is
developed, tested and documented, for people and for AI coding agents.

## Support

Please report bugs to the [GitHub Issues Page](https://github.com/smarter-sh/smarter-python/issues)
for this project.

## Contributing

Please see the [CONTRIBUTING](https://docs.smarter.sh/en/latest/smarter-framework/guides/contributing.html).
