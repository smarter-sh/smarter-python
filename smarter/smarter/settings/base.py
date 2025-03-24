"""
smarter-api base settings.
"""

import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("smarter.log"), logging.StreamHandler()],
)
