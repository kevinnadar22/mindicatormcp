"""Loguru logging setup."""

import sys

from loguru import logger

from app.core import config


def setup_logging() -> None:
    """Configure loguru sinks for the MCP process."""
    logger.remove()
    logger.add(
        sys.stderr,
        level=config.settings.log_level.upper(),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    )
    logger.bind(level=config.settings.log_level).info("logging configured")
