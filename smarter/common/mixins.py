"""Console helpers for formatting output."""

import logging

from .utils import formatted_text


logger = logging.getLogger(__name__)


class SmarterHelperMixin:
    """Mixin for smarter classes to provide helpful methods."""

    def __init__(self):
        logger.debug("Initializing %s()", self.formatted_class_name)

    @property
    def formatted_class_name(self):
        return formatted_text(self.__class__.__name__)
