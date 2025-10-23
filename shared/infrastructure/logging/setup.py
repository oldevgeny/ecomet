"""Loguru logging setup."""

import sys
from pathlib import Path

from loguru import logger


def setup_logging(
    log_level: str = "INFO",
    log_file: Path | None = None,
    json_logs: bool = False,
) -> None:
    """
    Configure loguru logger.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        json_logs: Whether to use JSON format for structured logging
    """
    # Remove default handler
    logger.remove()

    # Console handler
    if json_logs:
        logger.add(
            sys.stderr,
            level=log_level,
            serialize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",  # noqa: E501
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    # File handler (optional)
    if log_file:
        logger.add(
            log_file,
            level=log_level,
            rotation="10 MB",
            retention="1 week",
            compression="zip",
            serialize=json_logs,
            backtrace=True,
            diagnose=True,
        )

    logger.info(f"Logging configured: level={log_level}, json={json_logs}")
