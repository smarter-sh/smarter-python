# pylint: disable=E1101
"""A module containing constants for the OpenAI API."""
import importlib.util
import logging
import os
from pathlib import Path
from typing import Dict


logger = logging.getLogger(__name__)

SMARTER_ACCOUNT_NUMBER = "3141-5926-5359"
SMARTER_API_SUBDOMAIN = "api"
SMARTER_PLATFORM_SUBDOMAIN = "platform"
SMARTER_COMPANY_NAME = "Smarter"
SMARTER_EXAMPLE_CHATBOT_NAME = "example"
SMARTER_CUSTOMER_SUPPORT = "support@smarter.sh"

# The following are used in the React app
# to store the chatbot chat session key and debug mode settings
# as browser cookies. The React app has constants
# for these values as well which should be kept in sync.
SMARTER_CHAT_SESSION_KEY_NAME = "session_key"
SMARTER_DEFAULT_CACHE_TIMEOUT = 60 * 10  # 10 minutes

HERE = os.path.abspath(os.path.dirname(__file__))  # smarter/smarter/common
PROJECT_ROOT = str(Path(HERE).parent)  # smarter/smarter
PYTHON_ROOT = str(Path(PROJECT_ROOT).parent)  # smarter
REPO_ROOT = str(Path(PYTHON_ROOT).parent.parent)  # ./


def load_version() -> Dict[str, str]:
    """Stringify the __version__ module."""
    version_file_path = os.path.join(PROJECT_ROOT, "__version__.py")
    spec = importlib.util.spec_from_file_location("__version__", version_file_path)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    return version_module.__dict__


VERSION = load_version()


# pylint: disable=too-few-public-methods
class SmarterEnvironments:
    """A class representing the fixed set environments for the Smarter API."""

    LOCAL = "local"
    ALPHA = "alpha"
    BETA = "beta"
    NEXT = "next"
    PROD = "prod"
    all = [LOCAL, ALPHA, BETA, NEXT, PROD]
    aws_environments = [ALPHA, BETA, NEXT, PROD]
