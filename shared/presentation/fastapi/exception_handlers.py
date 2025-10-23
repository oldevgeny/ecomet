"""FastAPI exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from shared.domain.entities.exceptions import (
    ConfigurationError,
    DatabaseError,
    DomainError,
    RateLimitError,
    ScraperError,
    ValidationError,
)


async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:  # noqa: ARG001
    """
    Handle domain errors.

    Args:
        request: FastAPI request
        exc: Domain exception

    Returns:
        JSON error response
    """
    logger.error(f"Domain error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)},
    )


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:  # noqa: ARG001
    """
    Handle database errors.

    Args:
        request: FastAPI request
        exc: Database exception

    Returns:
        JSON error response
    """
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": "Database service unavailable", "detail": str(exc)},
    )


async def rate_limit_error_handler(request: Request, exc: RateLimitError) -> JSONResponse:  # noqa: ARG001
    """
    Handle rate limit errors.

    Args:
        request: FastAPI request
        exc: Rate limit exception

    Returns:
        JSON error response
    """
    logger.warning(f"Rate limit exceeded: {exc}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Rate limit exceeded", "detail": str(exc)},
    )


async def scraper_error_handler(request: Request, exc: ScraperError) -> JSONResponse:  # noqa: ARG001
    """
    Handle scraper errors.

    Args:
        request: FastAPI request
        exc: Scraper exception

    Returns:
        JSON error response
    """
    logger.error(f"Scraper error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"error": "External service error", "detail": str(exc)},
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:  # noqa: ARG001
    """
    Handle validation errors.

    Args:
        request: FastAPI request
        exc: Validation exception

    Returns:
        JSON error response
    """
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation error", "detail": str(exc)},
    )


async def configuration_error_handler(
    _: Request,
    exc: ConfigurationError,
) -> JSONResponse:
    """
    Handle configuration errors.

    Args:
        request: FastAPI request
        exc: Configuration exception

    Returns:
        JSON error response
    """
    logger.error(f"Configuration error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Configuration error", "detail": str(exc)},
    )


def register_exception_handlers(app: "FastAPI") -> None:
    """
    Register all exception handlers.

    Args:
        app: FastAPI application
    """
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(DatabaseError, database_error_handler)
    app.add_exception_handler(RateLimitError, rate_limit_error_handler)
    app.add_exception_handler(ScraperError, scraper_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(ConfigurationError, configuration_error_handler)
