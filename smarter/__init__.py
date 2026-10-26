"""
The Smarter Python SDK: the official Python client of the Smarter platform's api.

.. code-block:: python

    from smarter import Smarter

    client = Smarter()
    print(client.llm_clients.prompt(5, "Hello").text)

See https://docs.smarter.sh/en/latest/smarter-framework/smarter-python.html
"""

from .__version__ import __version__
from .client import Smarter
from .core.exceptions import (
    APIConnectionError,
    APIError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ResourceNotFoundError,
    SmarterConfigurationError,
    SmarterError,
    SmarterValueError,
    UnprocessableEntityError,
)
from .models.kinds import SAMKinds
from .models.manifest import Manifest
from .resources.llmclients import ChatSession, PromptStream, SmarterPromptError

__all__ = [
    "APIConnectionError",
    "APIError",
    "APIResponseValidationError",
    "APIStatusError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "ChatSession",
    "ConflictError",
    "InternalServerError",
    "Manifest",
    "NotFoundError",
    "PermissionDeniedError",
    "PromptStream",
    "RateLimitError",
    "SAMKinds",
    "ResourceNotFoundError",
    "Smarter",
    "SmarterConfigurationError",
    "SmarterError",
    "SmarterPromptError",
    "SmarterValueError",
    "UnprocessableEntityError",
    "__version__",
]
