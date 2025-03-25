# pylint: disable=W0401,F405
"""
smarter-api prod settings.
"""

from .base import *  # noqa


for handler in logging.root.handlers:
    handler.setLevel(logging.DEBUG)
