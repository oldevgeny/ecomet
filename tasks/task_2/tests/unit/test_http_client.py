"""Tests for HTTP client with rate limiting."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.domain.entities.exceptions import ScraperError
from tasks.task_2.infrastructure.http_client import RateLimitedHTTPClient


@pytest.fixture
def rate_limiter():
    limiter = AsyncMock()
    limiter.acquire = AsyncMock()
    limiter.release = AsyncMock()
    limiter.__aenter__ = AsyncMock(return_value=limiter)
    limiter.__aexit__ = AsyncMock()
    return limiter


@pytest.fixture
def http_client(rate_limiter):
    return RateLimitedHTTPClient(token="test_token", rate_limiter=rate_limiter)


async def test_http_client_context_manager(http_client):
    async with http_client as client:
        assert client._session is not None


async def test_http_client_get_success(http_client):
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.raise_for_status = MagicMock()

    async def mock_json():
        return {"test": "data"}

    mock_response.json = mock_json

    async with http_client:
        with patch.object(http_client._session, "get") as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response

            result = await http_client.get("https://api.github.com/test")

            assert result == {"test": "data"}
            mock_get.assert_called_once()


async def test_http_client_get_not_initialized(rate_limiter):
    client = RateLimitedHTTPClient(token="test_token", rate_limiter=rate_limiter)

    with pytest.raises(ScraperError, match="HTTP client is not initialized"):
        await client.get("https://api.github.com/test")


async def test_http_client_get_http_error(http_client, rate_limiter):
    import aiohttp

    async with http_client:
        with patch.object(http_client._session, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock(side_effect=aiohttp.ClientError("Request failed"))
            mock_get.return_value.__aenter__.return_value = mock_response

            with pytest.raises(ScraperError, match="HTTP request failed"):
                await http_client.get("https://api.github.com/test")

            rate_limiter.acquire.assert_called_once()
            rate_limiter.release.assert_called_once()


async def test_http_client_close_when_not_initialized(http_client):
    await http_client.close()


async def test_http_client_close_after_context(http_client):
    async with http_client:
        pass

    await http_client.close()
