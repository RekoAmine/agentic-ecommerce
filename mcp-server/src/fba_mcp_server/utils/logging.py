"""Logging configuration utilities."""

import logging


def configure_logging(level: str) -> None:
    """Configure process-wide structured-enough console logging."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
