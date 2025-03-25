"""
smarter-api Client.
"""

import json
import logging

from httpx import Client as httpx_Client
from httpx import Response as httpx_Response

from smarter.common.conf import settings as smarter_settings
from smarter.common.const import SmarterEnvironments
from smarter.common.mixins import SmarterHelperMixin


logger = logging.getLogger(__name__)


class Client(SmarterHelperMixin):
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
        print(f"{self.formatted_class_name}.post() url={url} headers={headers} data={data}")
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
        return (
            f"Client(api_key={self.api_key[-4:] if self.api_key and len(self.api_key) >= 4 else None}, "
            f"environment={self.environment})"
        )
