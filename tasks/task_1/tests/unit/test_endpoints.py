"""Unit tests for endpoints."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from shared.infrastructure.database.postgres_pool import PostgreSQLPool
from tasks.task_1.presentation.app import VERSION, create_app


@pytest.fixture
def mock_pool():
    return MagicMock(spec=PostgreSQLPool)


@pytest.fixture
def app_with_mock_pool(mock_pool):
    app = create_app()
    app.state.pool = mock_pool
    return app


@pytest.mark.anyio
async def test_health_endpoint_returns_healthy_status(app_with_mock_pool):
    async with AsyncClient(
        transport=ASGITransport(app=app_with_mock_pool),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == VERSION


@pytest.mark.anyio
async def test_db_version_endpoint_returns_version(app_with_mock_pool, mock_pool):
    mock_connection = AsyncMock()
    mock_connection.fetchval.return_value = "PostgreSQL 16.0"

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_connection
    mock_pool.acquire.return_value = mock_context

    async with AsyncClient(
        transport=ASGITransport(app=app_with_mock_pool),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/db_version")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["version"] == "PostgreSQL 16.0"
    mock_connection.fetchval.assert_called_once_with("SELECT version()")


@pytest.mark.anyio
async def test_db_version_endpoint_handles_pool_not_initialized():
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/db_version")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    data = response.json()
    assert "error" in data
    assert data["error"] == "Database service unavailable"
