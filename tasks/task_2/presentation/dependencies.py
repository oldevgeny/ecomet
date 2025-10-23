"""FastAPI dependencies for Task 2."""

from collections.abc import AsyncIterator

from fastapi import Request
from loguru import logger

from shared.domain.entities.exceptions import ScraperError
from shared.infrastructure.config.github import GitHubConfig
from shared.infrastructure.rate_limiting.composite_limiter import CompositeRateLimiter
from shared.infrastructure.rate_limiting.semaphore_limiter import SemaphoreRateLimiter
from shared.infrastructure.rate_limiting.token_bucket import TokenBucketRateLimiter
from tasks.task_2.infrastructure.github_scraper import GithubReposScrapper
from tasks.task_2.infrastructure.http_client import RateLimitedHTTPClient


def get_scraper(request: Request) -> GithubReposScrapper:
    """
    Get GitHub scraper from app state.

    Args:
        request: FastAPI request object

    Returns:
        GitHub scraper instance

    Raises:
        ScraperError: If scraper is not initialized
    """
    scraper = getattr(request.app.state, "scraper", None)
    if scraper is None:
        msg = "GitHub scraper is not initialized"
        raise ScraperError(msg)
    return scraper


async def get_http_client() -> AsyncIterator[RateLimitedHTTPClient]:
    """
    Dependency to get HTTP client with rate limiting.

    Yields:
        HTTP client

    Raises:
        ScraperError: If client creation fails
    """
    config = GitHubConfig()

    # Create composite rate limiter (MCR + RPS)
    rate_limiter = CompositeRateLimiter(
        [
            SemaphoreRateLimiter(max_concurrent=config.max_concurrent_requests),
            TokenBucketRateLimiter(rate=config.requests_per_second),
        ]
    )

    logger.debug("Creating HTTP client with rate limiting")
    async with RateLimitedHTTPClient(config.access_token, rate_limiter) as client:
        yield client
    logger.debug("HTTP client closed")
