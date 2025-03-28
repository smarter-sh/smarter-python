"""Console helpers for formatting output."""

import json
import logging
from functools import cached_property
from urllib.parse import urljoin

from cachetools import LRUCache
from httpx import Client as httpx_Client
from httpx import Response as httpx_Response  # copying openai api use of httpx for now.

from smarter.common.conf import settings as smarter_settings
from smarter.common.mixins import SmarterHelperMixin
from smarter.common.models.whoami import SmarterApiBaseModel, WhoAmIModel


logger = logging.getLogger(__name__)

# leaving this here for now as a reminder to to consider adding a disk-based
# persistent cache for the API responses. need to consider the trade-offs of
# using a disk-based cache and how this might affect installations on different
# operating systems, Kubernetes and other containerized environments, etc.
SMARTER_HELPER_MIXIN_CACHE = LRUCache(maxsize=smarter_settings.smarter_max_cache_size)
DEFAULT_API_ENDPOINT = "cli/whoami/"


class ApiBase(SmarterHelperMixin):
    """A class for working with the Smarter Api."""

    _api_key: str
    _timeout: int
    _client: httpx_Client
    _url_endpoint: str
    _httpx_response: httpx_Response
    _model_class: SmarterApiBaseModel = WhoAmIModel
    _model: SmarterApiBaseModel = None

    def __init__(
        self,
        api_key: str = None,
        url_endpoint: str = DEFAULT_API_ENDPOINT,
        model_class: SmarterApiBaseModel = None,
        timeout: int = None,
    ):
        """
        Initializes the class with the api key, url endpoint, and Pydantic model.
        We default to the WhoAmIModel if no model is provided so that Smarter()
        can be initialized without any arguments. The validate() method is probably
        no longer needed since we are using Pydantic models, but it doesn't hurt to keep it.
        """
        super().__init__()

        self._model_class: SmarterApiBaseModel = model_class or WhoAmIModel
        self._api_key = api_key or smarter_settings.smarter_api_key.get_secret_value()
        if not self.api_key:
            raise ValueError("api_key is required")
        self._timeout = timeout or smarter_settings.smarter_default_http_timeout
        self._client = httpx_Client(timeout=self.timeout)
        self._url_endpoint = url_endpoint
        self._httpx_response = self.post(url=self.url)
        self.validate()

        logger.debug("%s.__init__() base_url=%s", self.formatted_class_name, self.base_url)

    @property
    def model_class(self) -> SmarterApiBaseModel:
        """
        Returns the Pydantic model class.
        """
        return self._model_class

    @property
    def model(self) -> SmarterApiBaseModel:
        """
        Returns the Pydantic model instance.
        """
        if not self._model:
            if not self.httpx_response:
                raise ValueError("http response did not return any data.")
            self._model = self.model_class(**self.httpx_response.json())
        return self._model

    @cached_property
    def url(self) -> str:
        """
        Returns the full url for the smarter api.
        example: https://platform.smarter.sh/api/v1/cli/describe/chatbot/?name=netec-demo
        """
        return urljoin(self.base_url, self.url_endpoint)

    @cached_property
    def url_endpoint(self) -> str:
        """
        Returns the url endpoint for the smarter api.
        example: cli/describe/chatbot/?name=netec-demo
        """
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
        Validates the current client. We probably no longer need this since we are using pydantic models.
        """
        if not self.httpx_response:
            raise ValueError("http response did not return any data")
        json_data = self.to_json()
        if not json_data:
            raise ValueError("http response did not return any json data")

    @cached_property
    def httpx_response(self) -> httpx_Response:
        return self._httpx_response

    def to_json(self) -> dict:
        # return self.httpx_response.json()
        return self.model.model_dump()

    @cached_property
    def data(self) -> dict:
        """
        Returns the data from the Pydantic model. The structure of the data will depend on the model.
        This property should be overridden in subclasses.
        """
        return self.model.data

    @cached_property
    def api(self) -> str:
        """
        Returns the api from the Py
        example: smarter.sh/v1
        """
        return self.model.api

    @cached_property
    def thing(self) -> str:
        """
        Returns the thing from the Pydantic model. A 'kind' of manifest.
        example: chatbot
        """
        return self.model.thing

    @cached_property
    def metadata(self) -> str:
        """
        Returns the metadata from the Pydantic model.
        example: {"key": "314f94d110391787b282f7791fc810ac8ec852f748c074e8b7299506ebfd9bbc"}
        """
        return self.model.metadata.model_dump()

    @cached_property
    def message(self) -> str:
        """
        Returns the message from the Pydantic model. Usually this a human readable message
        generated by the API following CRUD operations, for the intended audience of cli users.
        """
        return self.model.message

    @cached_property
    def status(self) -> any:
        """
        Returns the status from the Pydantic model. This is a dict who's keys
        vary depending on the API endpoint and the state of the Api resource (e.g. chatbot, account, etc).
        """
        return self.model.status

    @cached_property
    def client(self) -> httpx_Client:
        """
        Returns the httpx client for managing http requests.
        """
        return self._client

    @cached_property
    def api_key(self) -> str:
        """
        Returns the api key for the Smarter API. This is required for all requests
        to the API.
        """
        return self._api_key

    @cached_property
    def timeout(self) -> int:
        """
        Returns the timeout for the httpx client.
        """
        return self._timeout

    @cached_property
    def base_url(self) -> str:
        """
        Returns the base url for the Smarter API. This is the root url for the API.
        example: https://platform.smarter.sh/api/v1/
        """
        return smarter_settings.environment_api_url

    def __del__(self):
        self.client.close()

    def __str__(self):
        api_key = self.api_key[-4:] if self.api_key and len(self.api_key) >= 4 else None
        return f"{self.formatted_class_name}(api_key={api_key}, environment={self.environment})"
