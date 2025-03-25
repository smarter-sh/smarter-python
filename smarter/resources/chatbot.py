"""
smarter-api Chatbot.
"""

import logging

from cachetools import TTLCache

from smarter.common.conf import settings as smarter_settings
from smarter.common.mixins import SmarterRequestHelper


logger = logging.getLogger(__name__)


class Chatbot(SmarterRequestHelper):
    """A class for working with Smarter Chatbots."""

    _name: str = None
    _chatbot_id: int = None
    _data: dict = None

    _cache = TTLCache(
        maxsize=smarter_settings.smarter_max_cache_size, ttl=smarter_settings.smarter_default_cache_timeout
    )

    def __new__(cls, chatbot_id: int = None, name: str = None):
        cache_key = chatbot_id or name
        if cache_key in cls._cache:
            logger.debug("Returning cached instance for key: %s", cache_key)
            return cls._cache[cache_key]

        instance = super().__new__(cls)
        cls._cache[cache_key] = instance
        return instance

    def __init__(self, chatbot_id: int = None, name: str = None):
        super().__init__()
        self._chatbot_id = chatbot_id
        self._name = name
        self.init()
        logger.debug("%s.__init__() chatbot_id=%s name=%s", self.formatted_class_name, self.chatbot_id, self.name)
        logger.debug("%s.__init__() data=%s", self.formatted_class_name, self.data)

    @property
    def name(self) -> str:
        return self._name

    @property
    def chatbot_id(self) -> int:
        return self._chatbot_id

    @property
    def data(self) -> dict:
        return self._data

    def init(self):
        """
        Initializes the chatbot.
        https://platform.smarter.sh/api/v1/cli/describe/chatbot/?name=netec-demo'
        """
        if not self.name:
            raise ValueError("Chatbot name is required")
        url = f"{self.base_url}cli/describe/chatbot/?name=" + self.name
        self._data = self.post(url=url, data={})

    def chat(self, message: str) -> dict:
        """
        Chat with the chatbot.
        """
        return self.post(
            f"/chatbots/{self.chatbot_id}/chat/",
            data={"message": message},
        )
