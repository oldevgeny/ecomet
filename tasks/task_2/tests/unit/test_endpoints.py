"""Tests for Task 2 endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from tasks.task_2.domain.entities import Repository, RepositoryAuthorCommitsNum
from tasks.task_2.presentation.app import create_app


@pytest.fixture
def mock_scraper():
    scraper = MagicMock()
    scraper.get_repositories = AsyncMock(
        return_value=[
            Repository(
                name="test-repo",
                owner="testuser",
                position=1,
                stars=1000,
                watchers=500,
                forks=200,
                language="Python",
                authors_commits_num_today=[RepositoryAuthorCommitsNum(author="John Doe", commits_num=5)],
            )
        ]
    )
    return scraper


@pytest.fixture
def app(mock_scraper):
    application = create_app()
    application.state.scraper = mock_scraper
    return application


async def test_get_repositories_endpoint(app, mock_scraper):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/repositories?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["repositories"]) == 1
    assert data["repositories"][0]["name"] == "test-repo"


async def test_get_repositories_with_custom_limit(app, mock_scraper):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/repositories?limit=50")

    assert response.status_code == 200
    mock_scraper.get_repositories.assert_called_once_with(50)


async def test_health_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
