"""
top-level test file for the smarter package.
"""

import unittest

from smarter.common.conf import settings as smarter_settings
from smarter.common.const import SmarterEnvironments


class TestSample(unittest.TestCase):
    """
    to verify that our codebase if free of syntax errors.
    """

    def test_example(self):
        self.assertEqual(1 + 1, 2)

    def test_settings(self):
        self.assertTrue(smarter_settings)
        self.assertEqual(smarter_settings.root_domain, "smarter.sh")
        self.assertEqual(smarter_settings.environment, SmarterEnvironments.LOCAL)


if __name__ == "__main__":
    unittest.main()
