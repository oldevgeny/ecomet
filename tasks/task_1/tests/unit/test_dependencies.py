"""Unit tests for dependencies."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Request

from shared.domain.entities.exceptions import DatabaseError
from shared.infrastructure.database.postgres_pool import PostgreSQLPool
from tasks.task_1.presentation.dependencies import get_pg_connection, get_pool


def test_get_pool_returns_pool_from_app_state():
    mock_pool = MagicMock(spec=PostgreSQLPool)
    mock_request = MagicMock(spec=Request)
    mock_request.app.state.pool = mock_pool

    result = get_pool(mock_request)

    assert result is mock_pool


def test_get_pool_raises_error_when_pool_not_initialized():
    mock_request = MagicMock(spec=Request)
    mock_request.app.state = MagicMock()
    del mock_request.app.state.pool

    with pytest.raises(DatabaseError, match="PostgreSQL pool is not initialized"):
        get_pool(mock_request)


@pytest.mark.anyio
async def test_get_pg_connection_yields_connection():
    mock_connection = AsyncMock()
    mock_pool = AsyncMock(spec=PostgreSQLPool)
    mock_pool.acquire.return_value.__aenter__.return_value = mock_connection

    connection_gen = get_pg_connection(mock_pool)
    connection = await connection_gen.__anext__()

    assert connection is mock_connection

    with pytest.raises(StopAsyncIteration):
        await connection_gen.__anext__()


@pytest.mark.anyio
async def test_get_pg_connection_properly_releases_connection():
    mock_connection = AsyncMock()
    mock_pool = AsyncMock(spec=PostgreSQLPool)
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_connection
    mock_pool.acquire.return_value = mock_context

    connection_gen = get_pg_connection(mock_pool)
    await connection_gen.__anext__()

    try:
        await connection_gen.__anext__()
    except StopAsyncIteration:
        pass

    mock_context.__aexit__.assert_called_once()
