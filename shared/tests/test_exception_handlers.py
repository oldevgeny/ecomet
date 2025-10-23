"""Tests for exception handlers."""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, status

from shared.domain.entities.exceptions import (
    ConfigurationError,
    DatabaseError,
    DomainError,
    RateLimitError,
    ScraperError,
    ValidationError,
)
from shared.presentation.fastapi.exception_handlers import (
    configuration_error_handler,
    database_error_handler,
    domain_error_handler,
    rate_limit_error_handler,
    register_exception_handlers,
    scraper_error_handler,
    validation_error_handler,
)


@pytest.mark.anyio
async def test_domain_error_handler() -> None:
    request = MagicMock()
    exc = DomainError("Test domain error")

    response = await domain_error_handler(request, exc)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "error" in response.body.decode()


@pytest.mark.anyio
async def test_database_error_handler() -> None:
    request = MagicMock()
    exc = DatabaseError("Test database error")

    response = await database_error_handler(request, exc)

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Database service unavailable" in response.body.decode()


@pytest.mark.anyio
async def test_rate_limit_error_handler() -> None:
    request = MagicMock()
    exc = RateLimitError("Test rate limit error")

    response = await rate_limit_error_handler(request, exc)

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Rate limit exceeded" in response.body.decode()


@pytest.mark.anyio
async def test_scraper_error_handler() -> None:
    request = MagicMock()
    exc = ScraperError("Test scraper error")

    response = await scraper_error_handler(request, exc)

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert "External service error" in response.body.decode()


@pytest.mark.anyio
async def test_validation_error_handler() -> None:
    request = MagicMock()
    exc = ValidationError("Test validation error")

    response = await validation_error_handler(request, exc)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Validation error" in response.body.decode()


@pytest.mark.anyio
async def test_configuration_error_handler() -> None:
    request = MagicMock()
    exc = ConfigurationError("Test configuration error")

    response = await configuration_error_handler(request, exc)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Configuration error" in response.body.decode()


def test_register_exception_handlers() -> None:
    app = FastAPI()

    register_exception_handlers(app)

    assert len(app.exception_handlers) >= 6
