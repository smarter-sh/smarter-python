"""Console helpers for formatting output."""

import json
import logging

from cachetools import LRUCache
from httpx import Client as httpx_Client
from httpx import Response as httpx_Response

from smarter.common.conf import settings as smarter_settings

from .utils import formatted_text


logger = logging.getLogger(__name__)

SMARTER_HELPER_MIXIN_CACHE = LRUCache(maxsize=smarter_settings.smarter_max_cache_size)


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
    _response: dict
    _response_data: dict

    def __new__(cls, api_key: str = None):
        cache_key = api_key or smarter_settings.smarter_api_key
        if cache_key and cache_key in SMARTER_HELPER_MIXIN_CACHE:
            logger.debug("Returning cached instance for api_key: %s", cache_key)
            return SMARTER_HELPER_MIXIN_CACHE[cache_key]

        instance = super().__new__(cls)
        SMARTER_HELPER_MIXIN_CACHE[cache_key] = instance
        return instance

    def __init__(self, api_key: str = None):
        super().__init__()

        if not api_key:
            api_key = smarter_settings.smarter_api_key
        if not api_key:
            raise ValueError("api_key is required")

        self._client = httpx_Client()
        self._api_key = api_key or smarter_settings.smarter_api_key
        self._response_data = None
        url = f"{self.base_url}cli/whoami/"
        self._response = self.post(url=url)
        self.validate()

        logger.debug("%s.__init__() base_url=%s", self.formatted_class_name, self.base_url)

    def get(self, url: str) -> httpx_Response:
        """
        Makes a get request to the smarter api
        """
        return self.client.get(url)

    def post(self, url: str, data: dict = None, headers=None) -> dict:
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
        if not self.response_data:
            raise ValueError("Invalid api_key")

        # validate the response_data response
        if not self.response_data:
            raise ValueError("no data was returned from http response")
        if not self.response_data:
            raise ValueError("'data' key is missing from http response")
        if not self.response_account:
            raise ValueError("'account' key is missing from http response")
        if not self.response_user:
            raise ValueError("'user' key is missing from http response")
        if not self.response_environment:
            raise ValueError("'environment' key is missing from http response")

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
    def base_url(self) -> str:
        return smarter_settings.environment_api_url

    @property
    def response_user(self) -> dict:
        retval = self.response_data.get("user")
        return retval

    @property
    def response_account(self) -> dict:
        retval = self.response_data.get("account")
        return retval

    @property
    def response_environment(self) -> str:
        retval = self.response_data.get("environment")
        return retval

    @property
    def response(self) -> dict:
        return self._response

    @property
    def response_data(self) -> dict:
        if not self._response_data:
            self._response_data = self.response.get("data")
        return self._response_data

    def __del__(self):
        self.client.close()

    def __str__(self):
        api_key = self.api_key[-4:] if self.api_key and len(self.api_key) >= 4 else None
        return f"{self.formatted_class_name}(api_key={api_key}, environment={self.environment})"
