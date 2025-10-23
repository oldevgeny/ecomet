"""Token bucket rate limiter implementation."""

import asyncio
import time

from loguru import logger

from shared.domain.entities.exceptions import RateLimitError


class TokenBucketRateLimiter:
    """Token bucket algorithm for rate limiting (RPS)."""

    def __init__(self, rate: int, burst: int | None = None) -> None:
        """
        Initialize token bucket rate limiter.

        Args:
            rate: Tokens per second (RPS)
            burst: Maximum burst size (defaults to rate)
        """
        self._rate = rate
        self._burst = burst or rate
        self._tokens = float(self._burst)
        self._last_update = time.monotonic()
        self._lock = asyncio.Lock()

        logger.debug(f"TokenBucketRateLimiter initialized: rate={rate}, burst={self._burst}")

    async def acquire(self) -> None:
        """
        Acquire a token (blocks if no tokens available).

        Raises:
            RateLimitError: If rate limit is exceeded
        """
        async with self._lock:
            await self._refill_tokens()

            if self._tokens < 1:
                wait_time = (1 - self._tokens) / self._rate
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                await self._refill_tokens()

            if self._tokens < 1:
                msg = "Rate limit exceeded after waiting"
                raise RateLimitError(msg)

            self._tokens -= 1
            logger.debug(f"Token acquired, remaining: {self._tokens:.2f}")

    async def release(self) -> None:
        """Release is a no-op for token bucket."""

    async def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_update

        new_tokens = elapsed * self._rate
        self._tokens = min(self._tokens + new_tokens, self._burst)
        self._last_update = now
