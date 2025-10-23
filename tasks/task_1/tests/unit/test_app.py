"""Tests for FastAPI application."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_app_lifespan_creates_and_closes_pool() -> None:
    async def mock_create_pool_func(*args, **kwargs):  # noqa: ANN002, ANN003
        return MagicMock()

    with patch("shared.infrastructure.database.postgres_pool.asyncpg.create_pool", side_effect=mock_create_pool_func):
        from tasks.task_1.presentation.app import create_app

        app = create_app()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"


def test_create_app_registers_routers() -> None:
    with (
        patch("tasks.task_1.presentation.app.setup_logging"),
        patch("tasks.task_1.presentation.app.register_exception_handlers"),
    ):
        from tasks.task_1.presentation.app import VERSION, create_app

        app = create_app()

        assert app.title == "E-Comet Task 1"
        assert app.version == VERSION
        assert len(app.routes) > 0
