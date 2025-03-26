"""
smarter-api Client.
"""

import logging

from smarter.common.mixins import ApiBase
from smarter.resources import Chatbot


logger = logging.getLogger(__name__)


class Chatbots:
    """
    A class for working with Smarter Chatbots.
    """

    request_helper: ApiBase = None

    def __init__(self, request_helper: ApiBase):
        self.request_helper = request_helper

    def get(self, chatbot_id: int = None, name: str = None) -> Chatbot:
        """
        Gets a chatbot by id.
        """
        return Chatbot(chatbot_id=chatbot_id, name=name)


class Resources:
    """A class for working with the Smarter Api resources."""

    request_helper: ApiBase = None

    def __init__(self, request_helper: ApiBase):
        self.request_helper = request_helper

    @property
    def chatbots(self) -> Chatbots:
        return Chatbots(request_helper=self.request_helper)


class Client(ApiBase):
    """A class for working with the Smarter Api."""

    _resources: Resources = None

    def __init__(self, api_key: str = None):
        super().__init__(api_key=api_key)
        self._resources: Resources = None

    @property
    def resources(self) -> Resources:
        if self._resources is None:
            self._resources = Resources(request_helper=self.request_helper)
        return self._resources
