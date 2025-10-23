"""Tests for Task 4 repository."""

from unittest.mock import AsyncMock

import pytest

from tasks.task_4.domain.entities import PhraseViews
from tasks.task_4.infrastructure.clickhouse.repository import QueryRepositoryImpl


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.fixture
def repository(mock_client):
    return QueryRepositoryImpl(client=mock_client)


async def test_get_phrase_views_by_hour(repository, mock_client):
    mock_client.fetch = AsyncMock(
        return_value=[
            {
                "phrase": "платье",
                "views_by_hour": [(12, 1), (13, 3), (14, 5)],
            },
            {
                "phrase": "туфли",
                "views_by_hour": [(12, 2), (13, 4)],
            },
        ]
    )

    result = await repository.get_phrase_views_by_hour(campaign_id=1111111)

    # Verify result structure and content
    assert len(result) == 2
    assert isinstance(result[0], PhraseViews)
    assert result[0].phrase == "платье"
    assert result[0].views_by_hour == [(12, 1), (13, 3), (14, 5)]
    assert result[1].phrase == "туфли"

    # Verify query contains campaign_id
    mock_client.fetch.assert_called_once()
    call_args = mock_client.fetch.call_args
    assert "campaign_id = 1111111" in call_args[0][0]


async def test_get_phrase_views_empty_result(repository, mock_client):
    mock_client.fetch = AsyncMock(return_value=[])

    result = await repository.get_phrase_views_by_hour(campaign_id=9999)

    assert len(result) == 0
