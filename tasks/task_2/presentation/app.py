"""FastAPI application for Task 2."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from loguru import logger

from shared.infrastructure.config.github import GitHubConfig
from shared.infrastructure.logging.setup import setup_logging
from shared.infrastructure.rate_limiting.composite_limiter import CompositeRateLimiter
from shared.infrastructure.rate_limiting.semaphore_limiter import SemaphoreRateLimiter
from shared.infrastructure.rate_limiting.token_bucket import TokenBucketRateLimiter
from shared.infrastructure.version import get_version_from_pyproject
from shared.presentation.fastapi.exception_handlers import register_exception_handlers
from shared.presentation.fastapi.health import create_health_router
from tasks.task_2.infrastructure.github_scraper import GithubReposScrapper
from tasks.task_2.infrastructure.http_client import RateLimitedHTTPClient
from tasks.task_2.presentation.endpoints import router

TASK_ROOT = Path(__file__).parent.parent
VERSION = get_version_from_pyproject(TASK_ROOT / "pyproject.toml")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan manager.

    Args:
        app: FastAPI application

    Yields:
        None
    """
    logger.info("Starting Task 2 application")

    # Initialize GitHub scraper
    config = GitHubConfig()
    rate_limiter = CompositeRateLimiter(
        SemaphoreRateLimiter(max_concurrent=config.max_concurrent_requests),
        TokenBucketRateLimiter(rate=config.requests_per_second),
    )

    async with RateLimitedHTTPClient(
        config.access_token.get_secret_value(),
        rate_limiter,
    ) as client:
        scraper = GithubReposScrapper(client, top_limit=config.top_repositories_limit)

        app.state.scraper = scraper
        app.state.client = client

        logger.info("GitHub scraper initialized")

        yield

    logger.info("Task 2 application shutdown complete")


def create_app() -> FastAPI:
    """
    Create FastAPI application.

    Returns:
        FastAPI application instance
    """
    setup_logging()

    app = FastAPI(
        title="E-Comet Task 2",
        version=VERSION,
        description="GitHub repositories scraper with rate limiting",
        lifespan=lifespan,
    )

    # Register routers
    app.include_router(router=create_health_router(version=VERSION))
    app.include_router(router)

    # Register exception handlers
    register_exception_handlers(app)

    return app
