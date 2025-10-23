"""Tests for Task 3 use cases."""

from unittest.mock import AsyncMock, patch

import pytest

from shared.infrastructure.config.clickhouse import ClickHouseConfig
from shared.infrastructure.database.clickhouse_client import ClickHouseClient
from tasks.task_2.domain.entities import Repository, RepositoryAuthorCommitsNum
from tasks.task_3.domain.use_cases import ScrapAndSaveUseCase


@pytest.fixture
def mock_scraper():
    scraper = AsyncMock()
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
                authors_commits_num_today=[
                    RepositoryAuthorCommitsNum(author="John Doe", commits_num=5),
                    RepositoryAuthorCommitsNum(author="Jane Smith", commits_num=3),
                ],
            )
        ]
    )
    return scraper


@pytest.fixture
def clickhouse_config():
    return ClickHouseConfig(
        host="localhost",
        port=9000,
        database="test",
        user="default",
        password="",
    )


@pytest.fixture
def use_case(mock_scraper, clickhouse_config):
    return ScrapAndSaveUseCase(scraper=mock_scraper, clickhouse_config=clickhouse_config)


async def test_scrape_and_save_execute(use_case, mock_scraper):
    # Create mock for ClickHouse client
    mock_ch_client = AsyncMock()
    mock_ch_client.execute = AsyncMock(return_value=None)

    async def mock_aenter(self):
        self._client = mock_ch_client
        return self

    async def mock_aexit(self, exc_type, exc_val, exc_tb):
        pass

    with patch.object(ClickHouseClient, "__aenter__", mock_aenter):  # noqa: SIM117
        with patch.object(ClickHouseClient, "__aexit__", mock_aexit):
            result = await use_case.execute(limit=10)

            assert result["total_repos"] == 1
            assert result["total_commits"] == 2
            mock_scraper.get_repositories.assert_called_once_with(10)
            # Should save repos, positions, and commits (3 batches)
            assert mock_ch_client.execute.call_count == 3


async def test_scrape_and_save_saves_repositories(use_case):
    mock_ch_client = AsyncMock()
    mock_ch_client.execute = AsyncMock(return_value=None)

    async def mock_aenter(self):
        self._client = mock_ch_client
        return self

    async def mock_aexit(self, exc_type, exc_val, exc_tb):
        pass

    with patch.object(ClickHouseClient, "__aenter__", mock_aenter):  # noqa: SIM117
        with patch.object(ClickHouseClient, "__aexit__", mock_aexit):
            await use_case.execute(limit=1)

            calls = mock_ch_client.execute.call_args_list
            assert len(calls) == 3

            # Check that repositories INSERT was called
            repos_call = str(calls[0])
            assert "INSERT INTO repositories" in repos_call
