# pylint: disable=W0401,W0614
"""
smarter-api local settings.
"""

import logging

from .base import *  # noqa


for handler in logging.root.handlers:
    handler.setLevel(logging.DEBUG)
