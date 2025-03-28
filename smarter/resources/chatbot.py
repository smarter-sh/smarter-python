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
    """
    A class for working with Smarter Chatbots. To do: initialize by chatbot_id
    """

    _name: str = None
    _chatbot_id: int = None

    def __init__(
        self,
        api_key: str = None,
        url_endpoint: str = None,
        chatbot_id: int = None,
        name: str = None,
        timeout: int = None,
    ):
        self._chatbot_id = chatbot_id
        self._name = name
        # to do: need to setup a more intelligent way to build the url_endpoint from known data.
        url_endpoint = url_endpoint or f"cli/describe/chatbot/?name={self.name}"
        super().__init__(api_key=api_key, url_endpoint=url_endpoint, model_class=ChatbotModel, timeout=timeout)
        logger.debug("%s.__init__() chatbot_id=%s name=%s", self.formatted_class_name, self.chatbot_id, self.name)

    def validate(self):
        """
        Validate the Smarter Api response body. Raise ValueError for any business rule violations that
        Pydantic would not be able to catch.
        """

        super().validate()

        # Validate the chatbot model. To do: need some MUCH better way to determine what the
        # api version is supposed to be.
        if self.model.api != "smarter.sh/v1":
            raise ValueError(f"Unsupported api version: {self.model.api}")

        # Validate that the manifest we received is for a chatbot.
        if self.model.data.kind != "Chatbot":
            raise ValueError(f"Received unexpected object kind: {self.model.data.kind}")

        # Validate that the chatbot name from the manifest matches the name that this class was initialized with.
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
        """
        Get the name of the chatbot.
        """
        return self._name

    @cached_property
    def chatbot_id(self) -> int:
        """
        Get the chatbot_id of the chatbot. Corresponds with the Django model id.
        """
        if not self._chatbot_id:
            sandbox_url_path = self.sandbox_url.path
            path = list(filter(None, sandbox_url_path.split("/")))
            self._chatbot_id = int(path[-1])
        return self._chatbot_id

    @cached_property
    def chatbot_metadata(self) -> dict:
        """
        Get the metadata of the chatbot.
        Deconstructs the metadata Pydantic model into a standard json dictionary.
        """
        return self.model.data.metadata.model_dump()

    @cached_property
    def chatbot_description(self) -> str:
        """
        Get the description of the chatbot from the manifest metadata.
        """
        return self.model.data.metadata.description

    @cached_property
    def chatbot_version(self) -> str:
        """
        Get the version of the chatbot from the manifest metadata.
        """
        return self.model.data.metadata.version

    @cached_property
    def spec(self) -> dict:
        """
        Get the spec of the chatbot from the manifest data.
        Deconstructs the spec Pydantic model into a standard json dictionary.
        """
        return self.model.data.spec.model_dump()

    @cached_property
    def config(self) -> dict:
        """
        Get the config of the chatbot from the manifest data.
        Deconstructs the config Pydantic model into a standard json dictionary.
        """
        return self.model.data.spec.config.model_dump()

    @cached_property
    def status(self) -> dict:
        """
        Get the status of the chatbot from the manifest data.
        Deconstructs the status Pydantic model into a standard json dictionary.
        """
        return self.model.data.status.model_dump()

    @cached_property
    def sandbox_url(self) -> ParseResult:
        """
        Get the sandbox URL of the chatbot from the manifest status and parse it.
        example: https://platform.smarter.sh/api/v1/chatbots/36/
        """
        url_string = self.model.data.status.sandboxUrl
        url_parsed = urlparse(url_string)
        return url_parsed

    @cached_property
    def url_chatapp(self) -> ParseResult:
        """
        Get the chatapp URL of the chatbot from the manifest status and parse it.
        example: https://netec-demo.3141-5926-5359.api.smarter.sh/chatapp/
        """
        url_string = self.model.data.status.urlChatapp
        url_parsed = urlparse(url_string)
        return url_parsed

    @cached_property
    def url_chatbot(self) -> ParseResult:
        """
        Get the chatbot URL of the chatbot from the manifest status and parse it.
        example: "https://platform.smarter.sh/api/v1/chatbots/36/chat/"
        """
        url_string = self.model.data.status.urlChatbot
        url_parsed = urlparse(url_string)
        return url_parsed

    def prompt(self, message: str, verbose: bool = False) -> dict:
        """
        Chat with the chatbot.
        # http://platform.smarter.sh/api/v1/cli/chat/netec-demo/?new_session=true&uid=admin
        """
        # to do: Smarter() should pass in the 'whoami' data (username, etc) to the Chatbot class.
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

        messages = prompt_response.data.response.data.body.smarter.messages
        for msg in messages:
            msg: MessageModel
            if msg.role == "assistant":
                return msg.content
        raise ValueError("No assistant message found in the prompt_response response.")
