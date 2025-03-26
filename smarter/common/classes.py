"""Console helpers for formatting output."""

import json
import logging
from functools import cached_property
from urllib.parse import urljoin

from cachetools import LRUCache
from httpx import Client as httpx_Client
from httpx import Response as httpx_Response
from pydantic import BaseModel

from smarter.common.conf import settings as smarter_settings
from smarter.common.const import SmarterJournalApiResponseKeys
from smarter.common.mixins import SmarterHelperMixin
from smarter.common.models.whoami import WhoAmIModel


logger = logging.getLogger(__name__)

SMARTER_HELPER_MIXIN_CACHE = LRUCache(maxsize=smarter_settings.smarter_max_cache_size)
DEFAULT_API_ENDPOINT = "cli/whoami/"


class ApiBase(SmarterHelperMixin):
    """A class for working with the Smarter Api."""

    _api_key: str
    _client: httpx_Client
    _url_endpoint: str
    _httpx_response: httpx_Response
    _model_class: BaseModel = WhoAmIModel
    _model_class_instance: BaseModel = None

    def __init__(self, api_key: str = None, url_endpoint: str = DEFAULT_API_ENDPOINT, model_class: BaseModel = None):
        super().__init__()

        self._model_class: BaseModel = model_class or WhoAmIModel
        self._client = httpx_Client()
        self._api_key = api_key or smarter_settings.smarter_api_key
        if not self.api_key:
            raise ValueError("api_key is required")
        self._url_endpoint = url_endpoint
        self._httpx_response = self.post(url=self.url)
        self.validate()

        logger.debug("%s.__init__() base_url=%s", self.formatted_class_name, self.base_url)

    @property
    def model(self) -> BaseModel:
        if not self._model_class_instance:
            self._model_class_instance = self._model_class(**self.to_json())
        return self._model_class_instance

    @cached_property
    def url(self) -> str:
        return urljoin(self.base_url, self.url_endpoint)

    @cached_property
    def url_endpoint(self) -> str:
        return self._url_endpoint

    def get(self, url: str) -> httpx_Response:
        """
        Makes a get request to the smarter api
        """
        return self.client.get(url)

    def post(self, url: str, data: dict = None, headers=None) -> httpx_Response:
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
        return response

    def validate(self):
        """
        Validates the current client
        """
        if not self.httpx_response:
            raise ValueError("http response did not return any data")
        json_data = self.to_json()
        if not json_data:
            raise ValueError("http response did not return any json data")

        for key in SmarterJournalApiResponseKeys.required:
            if key not in json_data.keys():
                raise ValueError(f"json http response data is missing key: {key}")

    @cached_property
    def httpx_response(self) -> httpx_Response:
        return self._httpx_response

    def to_json(self) -> dict:
        return self.httpx_response.json()

    @cached_property
    def data(self) -> dict:
        response_json = self.to_json()
        return response_json.get(SmarterJournalApiResponseKeys.DATA)

    @cached_property
    def api(self) -> str:
        response_json = self.to_json()
        return response_json.get(SmarterJournalApiResponseKeys.API)

    @cached_property
    def thing(self) -> str:
        response_json = self.to_json()
        return response_json.get(SmarterJournalApiResponseKeys.THING)

    @cached_property
    def metadata(self) -> str:
        response_json = self.to_json()
        return response_json.get(SmarterJournalApiResponseKeys.METADATA)

    @cached_property
    def message(self) -> str:
        response_json = self.to_json()
        return response_json.get(SmarterJournalApiResponseKeys.MESSAGE)

    @cached_property
    def status(self) -> any:
        response_json = self.to_json()
        return response_json.get(SmarterJournalApiResponseKeys.ERROR)

    @cached_property
    def client(self) -> httpx_Client:
        return self._client

    @cached_property
    def api_key(self) -> str:
        return self._api_key

    @cached_property
    def base_url(self) -> str:
        return smarter_settings.environment_api_url

    def __del__(self):
        self.client.close()

    def __str__(self):
        api_key = self.api_key[-4:] if self.api_key and len(self.api_key) >= 4 else None
        return f"{self.formatted_class_name}(api_key={api_key}, environment={self.environment})"
