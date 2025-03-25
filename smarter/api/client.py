"""
smarter-api Client.
"""

import logging

from cachetools import TTLCache

from smarter.common.conf import settings as smarter_settings
from smarter.common.mixins import SmarterRequestHelper
from smarter.resources import Chatbot


logger = logging.getLogger(__name__)


class Chatbots:
    """
    A class for working with Smarter Chatbots.
    """

    request_helper: SmarterRequestHelper = None

    def __init__(self, request_helper: SmarterRequestHelper):
        self.request_helper = request_helper

    def get(self, chatbot_id: int = None, name: str = None) -> Chatbot:
        """
        Gets a chatbot by id.
        """
        return Chatbot(chatbot_id=chatbot_id, name=name, request_helper=self.request_helper)


class Resources:
    """A class for working with the Smarter Api resources."""

    request_helper: SmarterRequestHelper = None

    def __init__(self, request_helper: SmarterRequestHelper):
        self.request_helper = request_helper

    @property
    def chatbots(self) -> Chatbots:
        return Chatbots(request_helper=self.request_helper)


class Client(SmarterRequestHelper):
    """A class for working with the Smarter Api."""

    _cache = TTLCache(
        maxsize=smarter_settings.smarter_max_cache_size, ttl=smarter_settings.smarter_default_cache_timeout
    )
    _resources: Resources = None

    def __new__(cls, api_key: str = None, environment: str = None):
        cache_key = api_key
        if cache_key in cls._cache:
            logger.debug("Returning cached instance for api key: %s", cache_key)
            return cls._cache[cache_key]

        instance = super().__new__(cls)
        cls._cache[cache_key] = instance
        return instance

    def __init__(self, api_key: str = None, environment: str = None):
        super().__init__(api_key, environment)
        self._resources: Resources = None

    @property
    def resources(self) -> Resources:
        if self._resources is None:
            self._resources = Resources(request_helper=self.request_helper)
        return self._resources
