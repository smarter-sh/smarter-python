"""Console helpers for formatting output."""

import json
import logging


logger = logging.getLogger(__name__)


def formatted_json(json_obj: json) -> str:
    pretty_json = json.dumps(json_obj, indent=4)
    return f"\033[32m{pretty_json}\033[0m"


def formatted_text(text: str) -> str:

    # bright green
    # return f"\033[92m{text}\033[0m"

    # regular green
    # return f"\033[32m{text}\033[0m"

    # dark red
    # return f"\033[31m{text}\033[0m"

    # bold and dark red
    return f"\033[1;31m{text}\033[0m"


def formatted_text_green(text: str) -> str:

    # bright green
    return f"\033[92m{text}\033[0m"


class SmarterHelperMixin:
    """Mixin for smarter classes to provide helpful methods."""

    def __init__(self):
        logger.debug("Initializing %s()", self.formatted_class_name)

    @property
    def formatted_class_name(self):
        return formatted_text(self.__class__.__name__)
