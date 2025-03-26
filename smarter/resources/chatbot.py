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
        if self.model.api != "smarter.sh/v1":
            raise ValueError(f"Unsupported api version: {self.model.api}")
        if self.model.data.kind != "Chatbot":
            raise ValueError(f"Received unexpected object kind: {self.model.data.kind}")
        if self.name:
            metadata_name = self.model.data.metadata.name
            if metadata_name != self.name:
                raise ValueError(f"Received unexpected chatbot name: {self.model.data.metadata.name}")

    @property
    def model(self) -> ChatbotModel:
        """
        Returns the Pydantic model instance.
        """
        if not self._model:
            if not self.httpx_response:
                raise ValueError("http response did not return any data.")
            self._model = self.model_class(**self.httpx_response.json())
        return self._model

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
        return self.model.data.metadata.model_dump()

    @cached_property
    def description(self) -> str:
        # return self.chatbot_metadata.get("description")
        return self.model.data.metadata.description

    @cached_property
    def version(self) -> str:
        # return self.chatbot_metadata.get("version")
        return self.model.data.metadata.version

    @cached_property
    def spec(self) -> dict:
        """
        Get the spec of the chatbot.
        """
        # return self.data.get("spec")
        return self.model.data.spec.model_dump()

    @cached_property
    def config(self) -> dict:
        """
        Get the config of the chatbot.
        """
        return self.model.data.spec.config.model_dump()

    @cached_property
    def status(self) -> dict:
        """
        Get the status of the chatbot.
        """
        # return self.data.get("status")
        return self.model.data.status.model_dump()

    @cached_property
    def sandbox_url(self) -> ParseResult:
        """
        Get the sandbox URL of the chatbot.
        """
        url_string = self.model.data.status.sandboxUrl
        url_parsed = urlparse(url_string)
        return url_parsed

    @cached_property
    def url_chatapp(self) -> ParseResult:
        """
        Get the chatapp URL of the chatbot.
        """
        url_string = self.model.data.status.urlChatapp
        url_parsed = urlparse(url_string)
        return url_parsed

    @cached_property
    def url_chatbot(self) -> ParseResult:
        """
        Get the chatbot URL of the chatbot.
        """
        url_string = self.model.data.status.urlChatbot
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
