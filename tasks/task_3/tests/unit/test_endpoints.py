"""Tests for Task 3 endpoints."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from tasks.task_3.presentation.app import create_app


@pytest.fixture
def mock_use_case():
    use_case = AsyncMock()
    use_case.execute = AsyncMock(
        return_value={
            "total_repos": 10,
            "total_commits": 50,
        }
    )
    return use_case


@pytest.fixture
def app(mock_use_case):
    application = create_app()
    application.state.use_case = mock_use_case
    return application


async def test_scrape_and_save_endpoint(app, mock_use_case):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/scrape-and-save?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_repos"] == 10
    assert data["total_commits"] == 50
    mock_use_case.execute.assert_called_once_with(limit=10)


async def test_health_endpoint(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
