"""
smarter-api Chatbot.
"""

import json
import logging
from functools import cached_property
from urllib.parse import ParseResult, urlparse

from smarter.common.classes import ApiBase
from smarter.resources.models.chatbot import ChatbotModel
from smarter.resources.models.prompt import MessageModel, PromptResponseModel


logger = logging.getLogger(__name__)


class Chatbot(ApiBase):
    """A class for working with Smarter Chatbots."""

    _name: str = None
    _chatbot_id: int = None

    def __init__(self, api_key: str = None, url_endpoint: str = None, chatbot_id: int = None, name: str = None):
        self._chatbot_id = chatbot_id
        self._name = name
        url_endpoint = url_endpoint or f"cli/describe/chatbot/?name={self.name}"
        super().__init__(api_key=api_key, url_endpoint=url_endpoint, model_class=ChatbotModel)
        logger.debug("%s.__init__() chatbot_id=%s name=%s", self.formatted_class_name, self.chatbot_id, self.name)

    def validate(self):

        # validate the structure and integrity of the Smarter Api response body
        super().validate()

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
        return self.chatbot_metadata.get("description")

    @cached_property
    def version(self) -> str:
        return self.chatbot_metadata.get("version")

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

    def prompt(self, message: str, verbose: bool = False) -> dict:
        """
        Chat with the chatbot.
        # http://platform.smarter.sh/api/v1/cli/chat/netec-demo/?new_session=true&uid=admin
        """
        username = "admin"
        url = self.base_url + f"cli/chat/{self.name}/?new_session=true&uid={username}"
        escaped_message = json.dumps(message)
        data = {
            "messages": [],
            "prompt": json.loads(escaped_message),
        }
        response = self.post(url=url, data=data)
        response_json: dict = response.json()
        prompt_response = PromptResponseModel(**response_json)

        if verbose:
            return prompt_response.model_dump()
        else:
            messages = prompt_response.data.response.data.body.smarter.messages
            for message in messages:
                message: MessageModel
                if message.role == "assistant":
                    return message.content
            raise ValueError("No assistant message found in the prompt_response response.")
