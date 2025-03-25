"""Console helpers for formatting output."""

import json
import logging

from httpx import Client as httpx_Client
from httpx import Response as httpx_Response

from smarter.common.conf import settings as smarter_settings
from smarter.common.const import SmarterEnvironments


logger = logging.getLogger(__name__)


def formatted_json(json_obj: json) -> str:
    pretty_json = json.dumps(json_obj, indent=4)
    return f"\033[32m{pretty_json}\033[0m"


def formatted_text(text: str) -> str:

    # bright green
    # return f"\033[92m{text}\033[0m"

    # regular green
    # return f"\033[32m{text}\033[0m"

    # dark red
    # return f"\033[31m{text}\033[0m"

    # bold and dark red
    return f"\033[1;31m{text}\033[0m"


def formatted_text_green(text: str) -> str:

    # bright green
    return f"\033[92m{text}\033[0m"


class SmarterHelperMixin:
    """Mixin for smarter classes to provide helpful methods."""

    def __init__(self):
        logger.debug("Initializing %s()", self.formatted_class_name)

    @property
    def formatted_class_name(self):
        return formatted_text(self.__class__.__name__)


class SmarterRequestHelper(SmarterHelperMixin):
    """A class for working with the Smarter Api."""

    _client: httpx_Client
    _api_key: str
    _environment: str = SmarterEnvironments.PROD
    _whoami: dict

    def __init__(self, api_key: str = None, environment: str = None):
        super().__init__()
        self._client = httpx_Client()
        self._api_key = api_key or smarter_settings.smarter_api_key
        self._environment = environment or self._environment
        self._whoami = None
        self.validate()
        logger.debug(
            "%s.__init__() base_url=%s environment=%s", self.formatted_class_name, self.base_url, self.environment
        )

    def get(self, url: str) -> httpx_Response:
        """
        Makes a get request to the smarter api
        """
        return self.client.get(url)

    def post(self, url: str, data: dict, headers=None) -> dict:
        """
        Makes a post request to the smarter api
        """
        headers = headers or {}
        headers["Authorization"] = f"Token {self.api_key}"
        logger.debug(
            "%s.post() url=%s headers=%s data=%s", self.formatted_class_name, url, json.dumps(headers, indent=4), data
        )
        response = self.client.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def validate(self):
        """
        Validates the current client
        """
        if not self.api_key:
            raise ValueError("api_key is required")
        if not self.environment:
            raise ValueError("environment is required")
        if not self.whoami:
            raise ValueError("Invalid api_key or environment")

    @property
    def request_helper(self):
        return self

    @property
    def client(self) -> httpx_Client:
        return self._client

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def environment(self) -> str:
        return self._environment

    @property
    def base_url(self) -> str:
        return smarter_settings.environment_api_url

    @property
    def whoami(self) -> dict:
        if self._whoami:
            return self._whoami
        url = f"{self.base_url}cli/whoami/"
        self._whoami = self.post(url=url, data=None)
        return self._whoami

    def __del__(self):
        self.client.close()

    def __str__(self):
        api_key = self.api_key[-4:] if self.api_key and len(self.api_key) >= 4 else None
        return f"{self.formatted_class_name}(api_key={api_key}, environment={self.environment})"
