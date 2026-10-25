"""
The base class of the SDK's unit tests.

The Smarter platform's tests subclass ``SmarterTestBase`` (ADR-013). The SDK's do too: this
``SmarterTestBase`` gives each test a :class:`smarter.Smarter` client whose requests never leave the
process. They are answered by an ``httpx.MockTransport`` from the routes that the test registers,
usually with the sanitized JSON of a real platform response from ``tests/data/``.
"""

import json
import os
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest import mock

import httpx

from smarter import Smarter
from smarter.core.typing import SmarterJsonType

DATA = Path(__file__).resolve().parent / "data"
API_KEY = "a" * 60 + "beef"
BASE_URL = "http://testserver"
API = f"{BASE_URL}/api/v1/"

Handler = Callable[[httpx.Request], httpx.Response]


class SmarterTestBase(unittest.TestCase):
    """
    A test whose client is answered by registered routes.

    The ``SMARTER_*`` environment variables and the smarter cli's configuration file are hidden
    from the client, so that a developer's own configuration can't change a test's result.
    """

    client: Smarter

    def setUp(self) -> None:
        super().setUp()
        environment = {key: value for key, value in os.environ.items() if not key.startswith("SMARTER_")}
        environment["SMARTER_CONFIG_FILE"] = str(DATA / "no-such-config.yaml")
        patcher = mock.patch.dict(os.environ, environment, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.routes: dict[tuple[str, str], Handler] = {}
        self.requests: list[httpx.Request] = []
        self.client = self.make_client()
        self.addCleanup(self.client.close)

    def make_client(self, **kwargs: Any) -> Smarter:
        """
        A client whose requests are answered by :meth:`handle`.

        :param kwargs: Arguments of :class:`smarter.Smarter`, which override the test's defaults.
        :returns: The client.
        """
        kwargs.setdefault("api_key", API_KEY)
        kwargs.setdefault("base_url", BASE_URL)
        kwargs.setdefault("max_retries", 0)
        http_client = httpx.Client(transport=httpx.MockTransport(self.handle))
        self.addCleanup(http_client.close)
        return Smarter(http_client=http_client, **kwargs)

    def handle(self, request: httpx.Request) -> httpx.Response:
        """Answer a request from its route, or with a 404 if it has none."""
        self.requests.append(request)
        handler = self.routes.get((request.method, request.url.path))
        if handler is None:
            return httpx.Response(404, json={"detail": f"no route for {request.method} {request.url.path}"})
        return handler(request)

    def route(
        self,
        method: str,
        path: str,
        *,
        json_body: SmarterJsonType = None,
        fixture: str | None = None,
        status: int = 200,
        text: str | None = None,
        headers: dict[str, str] | None = None,
        handler: Handler | None = None,
    ) -> None:
        """
        Answer requests to a path.

        :param method: The http method.
        :param path: The path, relative to ``/api/v1/``.
        :param json_body: The response's JSON.
        :param fixture: The name of a JSON file in ``tests/data/``, without ``.json``, as the response's JSON.
        :param status: The response's status.
        :param text: The response's text, instead of JSON.
        :param headers: The response's headers.
        :param handler: A function that answers the request, instead of a fixed response.
        """
        if handler is None:
            body = self.load_json(fixture) if fixture else json_body

            def fixed_response(_request: httpx.Request) -> httpx.Response:
                if text is not None:
                    return httpx.Response(status, text=text, headers=headers)
                return httpx.Response(status, json=body, headers=headers)

            handler = fixed_response

        self.routes[(method, f"/api/v1/{path.lstrip('/')}")] = handler

    @staticmethod
    def load_json(name: str) -> SmarterJsonType:
        """
        A JSON file of ``tests/data/``.

        :param name: The file's name, without ``.json``.
        :returns: Its content.
        """
        return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))

    @staticmethod
    def load_text(name: str) -> str:
        """
        A text file of ``tests/data/``.

        :param name: The file's name, with its extension.
        :returns: Its content.
        """
        return (DATA / name).read_text(encoding="utf-8")

    @property
    def last_request(self) -> httpx.Request:
        """The last request that the client sent."""
        return self.requests[-1]

    def request_json(self, index: int = -1) -> SmarterJsonType | None:
        """
        The JSON body of a request that the client sent.

        :param index: The request's index, the last by default.
        :returns: The parsed body.
        """
        return json.loads(self.requests[index].content)
