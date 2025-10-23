"""Tests for Task 4 endpoints."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from tasks.task_4.domain.entities import PhraseViews
from tasks.task_4.presentation.app import create_app


@pytest.fixture
def mock_use_case():
    use_case = AsyncMock()
    use_case.execute = AsyncMock(
        return_value=[
            PhraseViews(
                phrase="платье",
                views_by_hour=[(12, 1), (13, 3), (14, 5)],
            ),
        ]
    )
    return use_case


@pytest.fixture
def app(mock_use_case):
    application = create_app()
    application.state.use_case = mock_use_case
    return application


async def test_get_phrase_views_endpoint(app, mock_use_case):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/phrase-views?campaign_id=1111111")

    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == 1111111
    assert data["total_phrases"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["phrase"] == "платье"
    mock_use_case.execute.assert_called_once_with(1111111)


async def test_get_phrase_views_invalid_campaign_id(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/phrase-views?campaign_id=0")

    assert response.status_code == 422


async def test_health_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
