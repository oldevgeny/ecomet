"""Semaphore-based rate limiter for max concurrent requests."""

import asyncio

from loguru import logger


class SemaphoreRateLimiter:
    """Semaphore-based rate limiter for max concurrent requests (MCR)."""

    def __init__(self, max_concurrent: int) -> None:
        """
        Initialize semaphore rate limiter.

        Args:
            max_concurrent: Maximum concurrent operations
        """
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._max_concurrent = max_concurrent
        logger.debug(f"SemaphoreRateLimiter initialized: max_concurrent={max_concurrent}")

    async def acquire(self) -> None:
        """Acquire semaphore (blocks if max concurrent reached)."""
        await self._semaphore.acquire()
        logger.debug(f"Semaphore acquired, available: {self._semaphore._value}")

    async def release(self) -> None:
        """Release semaphore."""
        self._semaphore.release()
        logger.debug(f"Semaphore released, available: {self._semaphore._value}")
