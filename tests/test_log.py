"""Test smarter.core.log."""

import logging
import unittest
from unittest import mock

from smarter.core import log


class TestLog(unittest.TestCase):
    """Test the SDK's logging helpers."""

    def test_mask_secret(self):
        """A secret is reduced to its last four characters, and a short one to nothing."""
        self.assertEqual(log.mask_secret("a" * 60 + "beef"), "****beef")
        self.assertEqual(log.mask_secret("short"), "****")
        self.assertEqual(log.mask_secret(None), "None")

    def test_setup_logging(self):
        """SMARTER_LOG adds one stderr handler, at its level, once."""
        logger = logging.getLogger(log.ROOT_LOGGER_NAME)
        handlers, level = list(logger.handlers), logger.level
        self.addCleanup(setattr, logger, "handlers", handlers)
        self.addCleanup(logger.setLevel, level)
        with mock.patch.object(log, "_configured", False):
            log.setup_logging(None)
            self.assertEqual(logger.handlers, handlers)
            log.setup_logging("debug")
            self.assertEqual(logger.level, logging.DEBUG)
            self.assertEqual(len(logger.handlers), len(handlers) + 1)
            log.setup_logging("info")
            self.assertEqual(len(logger.handlers), len(handlers) + 1)
