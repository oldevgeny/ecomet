"""Tests for PostgreSQL pool."""

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
async def test_create_pool_successfully(postgres_config):
    mock_pool = MagicMock()

    async def mock_create_pool(*args, **kwargs):  # noqa: ANN002, ANN003
        return mock_pool

    with patch("shared.infrastructure.database.postgres_pool.asyncpg.create_pool", side_effect=mock_create_pool):
        pool_manager = PostgreSQLPool(postgres_config)
        await pool_manager.create_pool()

        assert pool_manager._pool is mock_pool


@pytest.mark.anyio
async def test_create_pool_raises_database_error_on_failure(postgres_config):
    with patch(
        "shared.infrastructure.database.postgres_pool.asyncpg.create_pool",
    ) as mock_create:
        mock_create.side_effect = Exception("Connection failed")

        pool_manager = PostgreSQLPool(postgres_config)

        with pytest.raises(DatabaseError, match="Failed to create PostgreSQL pool"):
            await pool_manager.create_pool()


@pytest.mark.anyio
async def test_close_pool_successfully(postgres_config):
    mock_pool = AsyncMock()

    pool_manager = PostgreSQLPool(postgres_config)
    pool_manager._pool = mock_pool

    await pool_manager.close_pool()

    mock_pool.close.assert_called_once()


@pytest.mark.anyio
async def test_acquire_returns_connection(postgres_config):
    mock_connection = AsyncMock()
    mock_pool = MagicMock()

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_connection
    mock_context.__aexit__.return_value = None
    mock_pool.acquire.return_value = mock_context

    pool_manager = PostgreSQLPool(postgres_config)
    pool_manager._pool = mock_pool

    async with pool_manager.acquire() as conn:
        assert conn is mock_connection


@pytest.mark.anyio
async def test_acquire_raises_error_when_pool_not_initialized(postgres_config):
    pool_manager = PostgreSQLPool(postgres_config)

    with pytest.raises(DatabaseError, match="Connection pool is not initialized"):
        async with pool_manager.acquire():
            pass


def test_pool_property_returns_pool(postgres_config):
    mock_pool = MagicMock()
    pool_manager = PostgreSQLPool(postgres_config)
    pool_manager._pool = mock_pool

    assert pool_manager.pool is mock_pool


def test_pool_property_raises_error_when_not_initialized(postgres_config):
    pool_manager = PostgreSQLPool(postgres_config)

    with pytest.raises(DatabaseError, match="Connection pool is not initialized"):
        _ = pool_manager.pool
