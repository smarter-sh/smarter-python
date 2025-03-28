"""
smarter-api Client.
"""

import logging
from functools import cached_property

from cachetools import LRUCache

from smarter.common.classes import ApiBase
from smarter.common.conf import settings as smarter_settings
from smarter.common.mixins import SmarterHelperMixin
from smarter.resources import Chatbot


logger = logging.getLogger(__name__)

RESOURCE_CACHE = LRUCache(maxsize=smarter_settings.smarter_max_cache_size)


class ResourceBaseClass(SmarterHelperMixin):
    """A class for working with the Smarter Api resources."""

    _api_key: str = None
    _timeout: int = None

    def __init__(self, api_key: str = None, timeout: int = None):
        super().__init__()
        self._api_key = api_key
        self._timeout = timeout

    @cached_property
    def api_key(self) -> str:
        return self._api_key

    @cached_property
    def timeout(self) -> int:
        return self._timeout

    def get_from_cache(self, cache_key: str) -> any:
        """
        Get a resource from the cache.
        """
        if cache_key in RESOURCE_CACHE:
            logger.debug("Cache hit for %s", cache_key)
            return RESOURCE_CACHE[cache_key]
        return None

    def save_to_cache(self, cache_key: str, resource: any) -> None:
        """
        Save a resource to the cache.
        """
        RESOURCE_CACHE[cache_key] = resource


class Chatbots(ResourceBaseClass):
    """
    A class for working with Smarter Chatbots.
    """

    def get(self, chatbot_id: int = None, name: str = None) -> Chatbot:
        """
        Gets a chatbot by id.
        """
        cache_key = self.cache_key(chatbot_id or name)
        chatbot = self.get_from_cache(cache_key)
        if chatbot:
            return chatbot
        chatbot = Chatbot(api_key=self.api_key, chatbot_id=chatbot_id, name=name, timeout=self.timeout)
        self.save_to_cache(cache_key, chatbot)
        return chatbot

    def cache_key(self, key_data) -> str:
        return f"Chatbot_{key_data}"


class Resources(ResourceBaseClass):
    """A class for working with the Smarter Api resources."""

    _chatbots: Chatbots = None

    def __init__(self, api_key: str = None, timeout: int = None):
        super().__init__(api_key=api_key, timeout=timeout)
        self._chatbots: Chatbots = None

    @cached_property
    def chatbots(self) -> Chatbots:
        if not self._chatbots:
            self._chatbots = Chatbots(api_key=self.api_key, timeout=self.timeout)
        return self._chatbots


class Smarter(ApiBase):
    """A class for working with the Smarter Api."""

    _resources: Resources = None

    def __init__(self, api_key: str = None, timeout: int = None):
        super().__init__(api_key=api_key, timeout=timeout)
        self._resources: Resources = None

    @cached_property
    def resources(self) -> Resources:
        if self._resources is None:
            self._resources = Resources(api_key=self.api_key, timeout=self.timeout)
        return self._resources
