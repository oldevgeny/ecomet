"""Tests for Task 2 dependencies."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from shared.domain.entities.exceptions import ScraperError
from tasks.task_2.infrastructure.github_scraper import GithubReposScrapper
from tasks.task_2.presentation.dependencies import get_http_client, get_scraper


class TestGetScraper:
    """Tests for get_scraper dependency."""

    def test_get_scraper_returns_instance(self):
        request = MagicMock()
        scraper = GithubReposScrapper(AsyncMock(), top_limit=100)
        request.app.state.scraper = scraper

        result = get_scraper(request)
        assert result is scraper

    def test_get_scraper_raises_when_not_initialized(self):
        request = MagicMock()
        request.app.state.scraper = None

        with pytest.raises(ScraperError, match="GitHub scraper is not initialized"):
            get_scraper(request)

    def test_get_scraper_raises_when_missing_attribute(self):
        request = MagicMock()
        del request.app.state.scraper

        with pytest.raises(ScraperError, match="GitHub scraper is not initialized"):
            get_scraper(request)


@pytest.mark.anyio
class TestGetHTTPClient:
    """Tests for get_http_client dependency."""

    async def test_get_http_client_yields_client(self, monkeypatch):
        monkeypatch.setenv("GITHUB_ACCESS_TOKEN", "test_token_123")

        generator = get_http_client()

        client = await generator.__anext__()
        assert client is not None
        assert hasattr(client, "get")

        await generator.aclose()
