"""Tests for Task 4 use cases."""

from unittest.mock import AsyncMock

import pytest

from tasks.task_4.domain.entities import PhraseViews
from tasks.task_4.domain.use_cases import GetPhraseViewsUseCase


@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.get_phrase_views_by_hour = AsyncMock(
        return_value=[
            PhraseViews(
                phrase="платье",
                views_by_hour=[(12, 1), (13, 3), (14, 5)],
            ),
            PhraseViews(
                phrase="туфли",
                views_by_hour=[(12, 2), (13, 4)],
            ),
        ]
    )
    return repo


@pytest.fixture
def use_case(mock_repository):
    return GetPhraseViewsUseCase(repository=mock_repository)


async def test_execute(use_case, mock_repository):
    result = await use_case.execute(campaign_id=1111111)

    assert len(result) == 2
    assert result[0].phrase == "платье"
    assert result[1].phrase == "туфли"
    mock_repository.get_phrase_views_by_hour.assert_called_once_with(1111111)


async def test_execute_empty_result(use_case, mock_repository):
    mock_repository.get_phrase_views_by_hour = AsyncMock(return_value=[])

    result = await use_case.execute(campaign_id=9999)

    assert len(result) == 0
