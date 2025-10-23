"""Extended tests for PostgreSQL pool."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.domain.entities.exceptions import DatabaseError
from shared.infrastructure.config.postgres import PostgresConfig
from shared.infrastructure.database.postgres_pool import PostgreSQLPool


@pytest.fixture
def postgres_config():
    return PostgresConfig(
        database_url="postgresql://user:pass@localhost:5432/testdb",
        min_pool_size=5,
        max_pool_size=10,
    )


@pytest.mark.anyio
async def test_close_pool_when_no_pool_exists(postgres_config) -> None:
    pool_manager = PostgreSQLPool(postgres_config)

    await pool_manager.close_pool()


@pytest.mark.anyio
async def test_acquire_connection_context_manager_error_handling(postgres_config) -> None:
    mock_pool = MagicMock()
    mock_context = AsyncMock()
    mock_context.__aenter__.side_effect = Exception("Connection error")
    mock_pool.acquire.return_value = mock_context

    pool_manager = PostgreSQLPool(postgres_config)
    pool_manager._pool = mock_pool

    with pytest.raises(DatabaseError, match="Failed to acquire database connection"):
        async with pool_manager.acquire():
            pass


@pytest.mark.anyio
async def test_create_pool_with_custom_settings(postgres_config) -> None:
    postgres_config.max_queries = 10000
    postgres_config.timeout = 30.0

    async def mock_create_pool_func(*args, **kwargs):  # noqa: ANN002, ANN003
        assert kwargs["max_queries"] == 10000
        assert kwargs["timeout"] == 30.0
        return MagicMock()

    with patch("shared.infrastructure.database.postgres_pool.asyncpg.create_pool", side_effect=mock_create_pool_func):
        pool_manager = PostgreSQLPool(postgres_config)
        await pool_manager.create_pool()
