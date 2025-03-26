"""
smarter-api Chatbot.
"""

import logging
from functools import cached_property
from urllib.parse import ParseResult, urlparse

from smarter.common.mixins import ApiBase


logger = logging.getLogger(__name__)


class Chatbot(ApiBase):
    """A class for working with Smarter Chatbots."""

    _name: str = None
    _chatbot_id: int = None
    _description: str = None
    _version: str = None

    def __init__(self, chatbot_id: int = None, name: str = None):
        self._chatbot_id = chatbot_id
        self._name = name
        url_endpoint = f"cli/describe/chatbot/?name={self.name}"
        super().__init__(url_endpoint=url_endpoint)
        logger.debug("%s.__init__() chatbot_id=%s name=%s", self.formatted_class_name, self.chatbot_id, self.name)

    def validate_httpx_response(self):

        # validate the structure and integrity of the Smarter Api response body
        super().validate_httpx_response()

        # validate the structure of the chatbot data
        chatbot_keys = ["apiVersion", "kind", "metadata", "spec", "status"]
        for key in self.data.keys():
            if key not in chatbot_keys:
                raise ValueError(f"Received an unexpected key: {key}")

        for key in chatbot_keys:
            if key not in self.data.keys():
                raise ValueError(f"Missing expected key: {key}")

        assert isinstance(self.chatbot_metadata, dict)
        assert isinstance(self.spec, dict)
        assert isinstance(self.status, dict)

        api_version = self.data.get("apiVersion")
        if api_version != "smarter.sh/v1":
            raise ValueError(f"Unsupported api version: {api_version}")
        kind = self.data.get("kind")
        if kind != "Chatbot":
            raise ValueError(f"Received unexpected object kind: {kind}")
        if self.name:
            metadata_name = self.chatbot_metadata.get("name")
            if metadata_name != self.name:
                raise ValueError(f"Received unexpected chatbot name: {metadata_name}")

    @cached_property
    def name(self) -> str:
        return self._name

    @cached_property
    def chatbot_id(self) -> int:
        if not self._chatbot_id:
            sandbox_url_path = self.sandbox_url.path
            path = list(filter(None, sandbox_url_path.split("/")))
            self._chatbot_id = int(path[-1])
        return self._chatbot_id

    @cached_property
    def chatbot_metadata(self) -> dict:
        return self.data.get("metadata")

    @cached_property
    def description(self) -> str:
        if not self._description:
            self._description = self.chatbot_metadata.get("description")
        return self._description

    @cached_property
    def version(self) -> str:
        if not self._version:
            self._version = self.chatbot_metadata.get("version")
        return self._version

    @cached_property
    def spec(self) -> dict:
        """
        Get the spec of the chatbot.
        """
        return self.data.get("spec")

    @cached_property
    def config(self) -> dict:
        """
        Get the config of the chatbot.
        """
        return self.spec.get("config")

    @cached_property
    def status(self) -> dict:
        """
        Get the status of the chatbot.
        """
        return self.data.get("status")

    @cached_property
    def sandbox_url(self) -> ParseResult:
        """
        Get the sandbox URL of the chatbot.
        """
        url_string = self.status.get("sandboxUrl")
        url_parsed = urlparse(url_string)
        return url_parsed

    @cached_property
    def url_chatapp(self) -> ParseResult:
        """
        Get the chatapp URL of the chatbot.
        """
        url_string = self.status.get("urlChatapp")
        url_parsed = urlparse(url_string)
        return url_parsed

    @cached_property
    def url_chatbot(self) -> ParseResult:
        """
        Get the chatbot URL of the chatbot.
        """
        url_string = self.status.get("urlChatbot")
        url_parsed = urlparse(url_string)
        return url_parsed

    def chat(self, message: str) -> dict:
        """
        Chat with the chatbot.
        """
        return self.post(
            f"/chatbots/{self.chatbot_id}/chat/",
            data={"message": message},
        )
