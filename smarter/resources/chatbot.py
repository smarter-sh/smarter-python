"""
smarter-api Chatbot.
"""

import logging
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
        super().validate_httpx_response()

        api_version = self.data["apiVersion"]
        if api_version != "smarter.sh/v1":
            raise ValueError(f"Unsupported api version: {api_version}")
        kind = self.data["kind"]
        if kind != "Chatbot":
            raise ValueError(f"Received unexpected object kind: {kind}")
        assert isinstance(self.chatbot_metadata, dict)
        metadata = self.data["metadata"]
        if self.name:
            if self.chatbot_metadata["name"] != self.name:
                raise ValueError(f"Received unexpected chatbot name: {metadata['name']}")

    @property
    def name(self) -> str:
        return self._name

    @property
    def chatbot_id(self) -> int:
        if not self._chatbot_id:
            sandbox_url_path = self.sandbox_url.path
            path = list(filter(None, sandbox_url_path.split("/")))
            self._chatbot_id = int(path[-1])
        return self._chatbot_id

    @property
    def chatbot_metadata(self) -> dict:
        return self.data["metadata"]

    @property
    def description(self) -> str:
        if not self._description:
            self._description = self.chatbot_metadata.get("description")
        return self._description

    @property
    def version(self) -> str:
        if not self._version:
            self._version = self.chatbot_metadata.get("version")
        return self._version

    @property
    def status(self) -> dict:
        """
        Get the status of the chatbot.
        """
        return self.data.get("status")

    @property
    def sandbox_url(self) -> ParseResult:
        """
        Get the sandbox URL of the chatbot.
        """
        url_string = self.status.get("sandboxUrl")
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
