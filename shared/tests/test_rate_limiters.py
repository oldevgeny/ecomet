"""Tests for rate limiters."""

import asyncio
import time

import pytest

from shared.infrastructure.rate_limiting.composite_limiter import CompositeRateLimiter
from shared.infrastructure.rate_limiting.semaphore_limiter import SemaphoreRateLimiter
from shared.infrastructure.rate_limiting.token_bucket import TokenBucketRateLimiter


@pytest.mark.anyio
async def test_semaphore_limiter_limits_concurrent_requests():
    limiter = SemaphoreRateLimiter(max_concurrent=2)
    acquired_count = 0
    max_acquired = 0

    async def acquire_and_release():
        nonlocal acquired_count, max_acquired
        await limiter.acquire()
        acquired_count += 1
        max_acquired = max(max_acquired, acquired_count)
        await asyncio.sleep(0.1)
        acquired_count -= 1
        await limiter.release()

    tasks = [acquire_and_release() for _ in range(5)]
    await asyncio.gather(*tasks)

    assert max_acquired == 2


@pytest.mark.anyio
async def test_token_bucket_limiter_enforces_rate_limit():
    limiter = TokenBucketRateLimiter(rate=5, burst=5)

    start_time = time.monotonic()

    for _ in range(10):
        await limiter.acquire()

    elapsed_time = time.monotonic() - start_time

    assert elapsed_time >= 1.0


@pytest.mark.anyio
async def test_token_bucket_allows_burst():
    limiter = TokenBucketRateLimiter(rate=5, burst=10)

    start_time = time.monotonic()

    for _ in range(10):
        await limiter.acquire()

    elapsed_time = time.monotonic() - start_time

    assert elapsed_time < 1.0


@pytest.mark.anyio
async def test_composite_limiter_applies_all_limiters():
    semaphore = SemaphoreRateLimiter(max_concurrent=2)
    token_bucket = TokenBucketRateLimiter(rate=10, burst=10)

    composite = CompositeRateLimiter(semaphore, token_bucket)

    await composite.acquire()
    await composite.release()


@pytest.mark.anyio
async def test_composite_limiter_enforces_strictest_limit():
    semaphore = SemaphoreRateLimiter(max_concurrent=1)
    token_bucket = TokenBucketRateLimiter(rate=100, burst=100)

    composite = CompositeRateLimiter(semaphore, token_bucket)

    acquired_count = 0
    max_acquired = 0

    async def task():
        nonlocal acquired_count, max_acquired
        await composite.acquire()
        acquired_count += 1
        max_acquired = max(max_acquired, acquired_count)
        await asyncio.sleep(0.05)
        acquired_count -= 1
        await composite.release()

    tasks = [task() for _ in range(3)]
    await asyncio.gather(*tasks)

    assert max_acquired == 1


@pytest.mark.anyio
async def test_token_bucket_release_is_noop():
    limiter = TokenBucketRateLimiter(rate=5, burst=5)
    await limiter.acquire()
    await limiter.release()
