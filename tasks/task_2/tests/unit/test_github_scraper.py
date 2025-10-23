"""Tests for GitHub scraper."""

from unittest.mock import AsyncMock

import pytest

from shared.domain.entities.exceptions import ScraperError
from tasks.task_2.infrastructure.github_scraper import GithubReposScrapper


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.fixture
def scraper(mock_client):
    return GithubReposScrapper(client=mock_client, top_limit=100)


async def test_scraper_get_repositories_success(scraper, mock_client):
    # Mock search response
    mock_client.get = AsyncMock(
        side_effect=[
            {
                "items": [
                    {
                        "name": "test-repo",
                        "owner": {"login": "testuser"},
                        "stargazers_count": 1000,
                        "watchers_count": 500,
                        "forks_count": 200,
                        "language": "Python",
                    }
                ]
            },
            # Mock commits response
            [{"commit": {"author": {"name": "John Doe"}}}],
        ]
    )

    repositories = await scraper.get_repositories(limit=1)

    assert len(repositories) == 1
    assert repositories[0].name == "test-repo"
    assert repositories[0].owner == "testuser"
    assert repositories[0].stars == 1000
    assert repositories[0].position == 1


async def test_scraper_get_repositories_with_commits(scraper, mock_client):
    mock_client.get = AsyncMock(
        side_effect=[
            {
                "items": [
                    {
                        "name": "test-repo",
                        "owner": {"login": "testuser"},
                        "stargazers_count": 1000,
                        "watchers_count": 500,
                        "forks_count": 200,
                        "language": "Python",
                    }
                ]
            },
            [
                {"commit": {"author": {"name": "John Doe"}}},
                {"commit": {"author": {"name": "John Doe"}}},
                {"commit": {"author": {"name": "Jane Smith"}}},
            ],
        ]
    )

    repositories = await scraper.get_repositories(limit=1)

    assert len(repositories[0].authors_commits_num_today) == 2
    assert repositories[0].authors_commits_num_today[0].author == "John Doe"
    assert repositories[0].authors_commits_num_today[0].commits_num == 2


async def test_scraper_handles_errors(scraper, mock_client):
    mock_client.get = AsyncMock(side_effect=Exception("API Error"))

    with pytest.raises(ScraperError, match="Failed to scrape repositories"):
        await scraper.get_repositories(limit=1)


async def test_scraper_filters_failed_repositories(scraper, mock_client):
    mock_client.get = AsyncMock(
        side_effect=[
            {
                "items": [
                    {
                        "name": "repo1",
                        "owner": {"login": "user1"},
                        "stargazers_count": 100,
                        "watchers_count": 50,
                        "forks_count": 20,
                        "language": "Python",
                    },
                    {
                        "name": "repo2",
                        "owner": {"login": "user2"},
                        "stargazers_count": 200,
                        "watchers_count": 100,
                        "forks_count": 40,
                        "language": "Go",
                    },
                ]
            },
            [{"commit": {"author": {"name": "Author1"}}}],
            Exception("Failed to fetch commits"),
        ]
    )

    repositories = await scraper.get_repositories(limit=2)

    assert len(repositories) == 1
    assert repositories[0].name == "repo1"
