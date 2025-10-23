"""Rate limiter protocols."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class RateLimiter(Protocol):
    """Protocol for rate limiting."""

    async def acquire(self) -> None:
        """Acquire permission to proceed (blocking if rate limit exceeded)."""

    async def release(self) -> None:
        """Release the acquired permission."""
