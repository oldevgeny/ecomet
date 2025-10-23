"""Tests for logging setup."""

from pathlib import Path
from unittest.mock import patch

from shared.infrastructure.logging.setup import setup_logging


def test_setup_logging_with_defaults() -> None:
    with patch("shared.infrastructure.logging.setup.logger") as mock_logger:
        setup_logging()

        assert mock_logger.remove.called
        assert mock_logger.add.called


def test_setup_logging_with_json_format() -> None:
    with patch("shared.infrastructure.logging.setup.logger") as mock_logger:
        setup_logging(log_level="DEBUG", json_logs=True)

        mock_logger.add.assert_called()
        call_kwargs = mock_logger.add.call_args_list[0][1]
        assert call_kwargs.get("serialize") is True
        assert call_kwargs.get("level") == "DEBUG"


def test_setup_logging_with_file() -> None:
    log_file = Path("/tmp/test.log")

    with patch("shared.infrastructure.logging.setup.logger") as mock_logger:
        setup_logging(log_file=log_file)

        assert mock_logger.add.call_count >= 2
