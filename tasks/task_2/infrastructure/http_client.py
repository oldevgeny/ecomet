"""HTTP client with rate limiting for GitHub API."""

from typing import Any

import aiohttp
from loguru import logger

from shared.domain.entities.exceptions import ScraperError
from shared.domain.protocols.rate_limiter import RateLimiter


class RateLimitedHTTPClient:
    """HTTP client with rate limiting."""

    def __init__(self, token: str, rate_limiter: RateLimiter) -> None:
        """
        Initialize HTTP client.

        Args:
            token: GitHub access token
            rate_limiter: Rate limiter for requests
        """
        self._token = token
        self._rate_limiter = rate_limiter
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> "RateLimitedHTTPClient":
        """Enter async context."""
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self._session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:  # noqa: ANN401
        """Exit async context."""
        await self.close()

    async def get(self, url: str, **kwargs: Any) -> dict[str, Any]:  # noqa: ANN401
        """
        Make GET request with rate limiting.

        Args:
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            JSON response

        Raises:
            ScraperError: If request fails
        """
        if not self._session:
            msg = "HTTP client is not initialized"
            raise ScraperError(msg)

        await self._rate_limiter.acquire()
        try:
            logger.debug(f"Making GET request to {url}")
            async with self._session.get(url, **kwargs) as response:
                response.raise_for_status()
                data = await response.json()
                logger.debug(f"Successfully fetched data from {url}")
                return data
        except aiohttp.ClientError as exc:
            error_msg = f"HTTP request failed: {exc}"
            logger.error(error_msg)
            raise ScraperError(error_msg) from exc
        finally:
            await self._rate_limiter.release()

    async def close(self) -> None:
        """Close HTTP client session."""
        if self._session:
            await self._session.close()
            logger.debug("HTTP client session closed")
