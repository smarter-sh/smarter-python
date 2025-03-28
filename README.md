# Smarter Python API library

[![PyPI version](https://img.shields.io/pypi/v/smarter.svg)](https://pypi.org/project/smarter-api/)
[![Unit Tests](https://github.com/QueriumCorp/smarter/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/QueriumCorp/smarter/actions/workflows/releaseController.yml)
![Release Status](https://github.com/QueriumCorp/smarter/actions/workflows/release.yml/badge.svg?branch=main)
![Auto Assign](https://github.com/QueriumCorp/smarter/actions/workflows/auto-assign.yml/badge.svg)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![hack.d Lawrence McDaniel](https://img.shields.io/badge/hack.d-Lawrence%20McDaniel-orange.svg)](https://lawrencemcdaniel.com)

The Smarter Python library provides convenient access to the Smarter REST API from any Python 3.8+
application. The library includes type definitions for all request params and response fields.

## Documentation

The REST API documentation can be found on [platform.smarter.sh](https://platform.smarter.sh/docs/api/).

## Installation

```sh
# install from PyPI
pip install smarter-api
```

## Usage

The primary API for interacting with Smarter models is the [cli](https://platform.smarter.sh/docs/swagger/). You can generate text from the model with the code below.

```python
import os
from smarter import Smarter

client = Smarter(
    # This is the default and can be omitted
    api_key=os.environ.get("SMARTER_API_KEY"),
    # This is the default and can be omitted
    timeout=60
)

chatbot = client.resources.chatbots.get(name="my-chatbot")
chat = chatbot.prompt("Hello, World!")

print(chat)
```

While you can provide an `api_key` keyword argument,
we recommend using [python-dotenv](https://pypi.org/project/python-dotenv/)
to add `SMARTER_API_KEY="My API Key"` to your `.env` file
so that your API key is not stored in source control.
[Get an API key here](https://platform.smarter.sh/dashboard/account/dashboard/api-keys/).

## Using types

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev) which also provide helper methods for things like:

- Serializing back into JSON, `model.to_json()`
- Converting to a dictionary, `model.to_dict()`

Typed requests and responses provide autocomplete and documentation within your editor. If you would like to see type errors in VS Code to help catch bugs earlier, set `python.analysis.typeCheckingMode` to `basic`.

## Pagination

List methods in the Smarter API are paginated.

This library provides auto-paginating iterators with each list response, so you do not have to request successive pages manually:

```python
from smarter import Smarter

client = Smarter()

all_jobs = []
# Automatically fetches more pages as needed.
for job in client.fine_tuning.jobs.list(
    limit=20,
):
    # Do something with job here
    all_jobs.append(job)
print(all_jobs)
```

Alternatively, you can use the `.has_next_page()`, `.next_page_info()`, or `.get_next_page()` methods for more granular control working with pages:

```python
first_page = await client.fine_tuning.jobs.list(
    limit=20,
)
if first_page.has_next_page():
    print(f"will fetch next page using these details: {first_page.next_page_info()}")
    next_page = await first_page.get_next_page()
    print(f"number of items we just fetched: {len(next_page.data)}")
```

Or just work directly with the returned data:

## Nested params

Nested parameters are dictionaries, typed using `TypedDict`, for example:

```python
from smarter import Smarter

client = Smarter()

response = client.chat.responses.create(
    input=[
        {
            "role": "user",
            "content": "How much ?",
        }
    ],
    model="gpt-4o",
    response_format={"type": "json_object"},
)
```

## File uploads

Request parameters that correspond to file uploads can be passed as `bytes`, a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance or a tuple of `(filename, contents, media type)`.

```python
from pathlib import Path
from smarter import Smarter

client = Smarter()

client.files.create(
    file=Path("input.jsonl"),
    purpose="fine-tune",
)
```

The async client uses the exact same interface. If you pass a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance, the file contents will be read asynchronously automatically.

## Handling errors

When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of `smarter.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx
response), a subclass of `smarter.APIStatusError` is raised, containing `status_code` and `response` properties.

All errors inherit from `smarter.APIError`.

```python
import smarter
from smarter import Smarter

client = Smarter()

try:
    client.fine_tuning.jobs.create(
        model="gpt-4o",
        training_file="file-abc123",
    )
except smarter.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except smarter.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except smarter.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

Error codes are as follows:

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |

## Request IDs

> For more information on debugging requests, see [these docs](https://platform.smarter.sh/docs/api/)

All object responses in the SDK provide a `_request_id` property which is added from the `x-request-id` response header so that you can quickly log failing requests and report them back to Smarter.

```python
response = await client.responses.create(
    model="gpt-4o-mini",
    input="Say 'this is a test'.",
)
print(response._request_id)  # req_123
```

Note that unlike other properties that use an `_` prefix, the `_request_id` property
_is_ public. Unless documented otherwise, _all_ other `_` prefix properties,
methods and modules are _private_.

> [!IMPORTANT]
> If you need to access request IDs for failed requests you must catch the `APIStatusError` exception

```python
import smarter

try:
    completion = await client.chat.completions.create(
        messages=[{"role": "user", "content": "Say this is a test"}], model="gpt-4"
    )
except smarter.APIStatusError as exc:
    print(exc.request_id)  # req_123
    raise exc
```

## Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff.
Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict,
429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable retry settings:

```python
from smarter import Smarter

# Configure the default for all requests:
client = Smarter(
    # default is 2
    max_retries=0,
)

# Or, configure per-request:
client.with_options(max_retries=5).chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How can I get the name of the current day in JavaScript?",
        }
    ],
    model="gpt-4o",
)
```

## Timeouts

By default requests time out after 10 minutes. You can configure this with a `timeout` option,
which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/timeouts/#fine-tuning-the-configuration) object:

```python
from smarter import Smarter

# Configure the default for all requests:
client = Smarter(
    # 20 seconds (default is 10 minutes)
    timeout=20.0,
)

# More granular control:
client = Smarter(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Override per-request:
client.with_options(timeout=5.0).chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "How can I list all files in a directory using Python?",
        }
    ],
    model="gpt-4o",
)
```

On timeout, an `APITimeoutError` is thrown.

Note that requests that time out are [retried twice by default](#retries).

## Advanced

### Logging

We use the standard library [`logging`](https://docs.python.org/3/library/logging.html) module.

You can enable logging by setting the environment variable `SMARTER_LOG` to `info`.

```shell
$ export SMARTER_LOG=info
```

Or to `debug` for more verbose logging.

### How to tell whether `None` means `null` or missing

In an API response, a field may be explicitly `null`, or missing entirely; in either case, its value is `None` in this library. You can differentiate the two cases with `.model_fields_set`:

```python
if response.my_field is None:
  if 'my_field' not in response.model_fields_set:
    print('Got json like {}, without a "my_field" key present at all.')
  else:
    print('Got json like {"my_field": null}.')
```

### Configuring the HTTP client

You can directly override the [httpx client](https://www.python-httpx.org/api/#client) to customize it for your use case, including:

- Support for [proxies](https://www.python-httpx.org/advanced/proxies/)
- Custom [transports](https://www.python-httpx.org/advanced/transports/)
- Additional [advanced](https://www.python-httpx.org/advanced/clients/) functionality

```python
import httpx
from smarter import Smarter

client = Smarter(
    # Or use the `SMARTER_BASE_URL` env var
    base_url="http://my.test.server.example.com:8083/v1",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

### Managing HTTP resources

By default the library closes underlying HTTP connections whenever the client is [garbage collected](https://docs.python.org/3/reference/datamodel.html#object.__del__). You can manually close the client using the `.close()` method if desired, or with a context manager that closes when exiting.

```python
from smarter import Smarter

with Smarter() as client:
  # make requests here
  ...

# HTTP client is now closed
```

## Versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals.)_
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://github.com/smarter-sh/smarter-python/issues) with questions, bugs, or suggestions.

### Determining the installed version

If you've upgraded to the latest version but aren't seeing any new features you were expecting then your python environment is likely still using an older version.

You can determine the version that is being used at runtime with:

```python
import smarter
print(smarter.__version__)
```

## Requirements

Python 3.8 or higher.

## Contributing

See [the contributing documentation](./doc/CONTRIBUTING.md).
