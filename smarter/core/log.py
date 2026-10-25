"""
Logging for the Smarter SDK.

The SDK logs to the ``smarter`` logger hierarchy (``smarter.client``, ``smarter.resources...``) and,
as a library should, adds no handlers unless asked to. Set ``SMARTER_LOG=info`` to log each
request's method, url, status and duration to stderr, or ``SMARTER_LOG=debug`` to log their bodies
too. Or configure the ``smarter`` logger as you would any other.

The Smarter platform controls its logging per module with waffle switches (ADR-011). The SDK's
equivalent is the logger hierarchy: e.g. ``logging.getLogger("smarter.client").setLevel(...)``.

Api keys are never logged: see :func:`mask_secret`.
"""

import logging

ROOT_LOGGER_NAME = "smarter"
_configured = False


def mask_secret(secret: str | None) -> str:
    """
    A secret, masked for logging: its last four characters.

    :param secret: The secret, e.g. an api key.
    :returns: e.g. ``****5150``, or ``None``.
    """
    if not secret:
        return "None"
    return "****" + secret[-4:] if len(secret) > 8 else "****"


def setup_logging(level: str | None) -> None:
    """
    Log the SDK's messages to stderr, at the given level, once per process.

    :param level: ``debug`` or ``info``, or None to leave logging as it is.
    """
    global _configured  # pylint: disable=global-statement
    if not level or _configured:
        return
    logger = logging.getLogger(ROOT_LOGGER_NAME)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if level == "debug" else logging.INFO)
    _configured = True


__all__ = ["ROOT_LOGGER_NAME", "mask_secret", "setup_logging"]
