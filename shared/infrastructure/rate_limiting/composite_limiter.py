"""Composite rate limiter combining multiple strategies."""

from loguru import logger

from shared.domain.protocols.rate_limiter import RateLimiter


class CompositeRateLimiter:
    """Composite rate limiter that combines multiple limiters."""

    def __init__(self, *limiters: RateLimiter) -> None:
        """
        Initialize composite rate limiter.

        Args:
            *limiters: Multiple rate limiters to combine
        """
        self._limiters = limiters
        logger.debug(f"CompositeRateLimiter initialized with {len(limiters)} limiters")

    async def acquire(self) -> None:
        """Acquire all limiters in sequence."""
        for limiter in self._limiters:
            await limiter.acquire()

    async def release(self) -> None:
        """Release all limiters in reverse sequence."""
        for limiter in reversed(self._limiters):
            await limiter.release()
