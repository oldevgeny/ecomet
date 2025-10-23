"""Tests for application lifespan."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.infrastructure.config.postgres import PostgresConfig


@pytest.mark.anyio
async def test_lifespan_startup_and_shutdown() -> None:
    from fastapi import FastAPI

    from tasks.task_1.presentation.app import lifespan

    app = FastAPI()
    mock_pool = MagicMock()

    async def mock_create_pool_func(*args, **kwargs):  # noqa: ANN002, ANN003
        return mock_pool

    with (
        patch("tasks.task_1.presentation.app.PostgresConfig") as mock_config,
        patch("tasks.task_1.presentation.app.PostgreSQLPool") as mock_pool_class,
        patch("shared.infrastructure.database.postgres_pool.asyncpg.create_pool", side_effect=mock_create_pool_func),
    ):
        mock_config.return_value = PostgresConfig(
            database_url="postgresql://user:pass@localhost:5432/testdb",
        )

        pool_instance = MagicMock()
        pool_instance.create_pool = AsyncMock()
        pool_instance.close_pool = AsyncMock()
        mock_pool_class.return_value = pool_instance

        async with lifespan(app):
            assert hasattr(app.state, "pool")

        pool_instance.create_pool.assert_called_once()
        pool_instance.close_pool.assert_called_once()
