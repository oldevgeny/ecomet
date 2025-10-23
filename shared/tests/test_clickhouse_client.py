"""Tests for ClickHouse client."""

from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientSession

from shared.domain.entities.exceptions import DatabaseError
from shared.infrastructure.config.clickhouse import ClickHouseConfig
from shared.infrastructure.database.clickhouse_client import (
    ClickHouseClient,
    validate_sql_identifier,
)


class TestValidateSQLIdentifier:
    """Tests for SQL identifier validation."""

    def test_valid_simple_identifier(self):
        validate_sql_identifier("table_name")
        validate_sql_identifier("_private")
        validate_sql_identifier("Table123")

    def test_valid_qualified_identifier(self):
        validate_sql_identifier("database.table", allow_qualified=True)
        validate_sql_identifier("db.tbl", allow_qualified=True)

    def test_invalid_simple_identifier(self):
        with pytest.raises(DatabaseError, match="Invalid SQL identifier"):
            validate_sql_identifier("123table")

        with pytest.raises(DatabaseError, match="Invalid SQL identifier"):
            validate_sql_identifier("table-name")

        with pytest.raises(DatabaseError, match="Invalid SQL identifier"):
            validate_sql_identifier("table name")

    def test_invalid_qualified_identifier(self):
        with pytest.raises(DatabaseError, match="Invalid SQL identifier"):
            validate_sql_identifier("database.table")

        with pytest.raises(DatabaseError, match="Invalid SQL identifier"):
            validate_sql_identifier("db.table.column", allow_qualified=True)


@pytest.mark.anyio
class TestClickHouseClient:
    """Tests for ClickHouse client."""

    @pytest.fixture
    def config(self):
        return ClickHouseConfig(
            host="localhost",
            port=8123,
            user="default",
            password="secret",
            database="test_db",
            batch_size=1000,
        )

    @pytest.fixture
    def mock_session(self):
        session = AsyncMock(spec=ClientSession)
        session.closed = False
        session.close = AsyncMock()
        return session

    @pytest.fixture
    def mock_ch_client(self):
        client = AsyncMock()
        client.execute = AsyncMock(return_value="OK")
        client.fetch = AsyncMock(return_value=[{"id": 1}, {"id": 2}])
        return client

    async def test_context_manager_successful_initialization(self, config, mock_session, mock_ch_client):
        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            async with ClickHouseClient(config) as client:
                assert client._client is not None
                assert client._session is not None

            mock_session.close.assert_called_once()

    async def test_context_manager_initialization_failure(self, config):
        with (
            patch(
                "shared.infrastructure.database.clickhouse_client.ClientSession",
                side_effect=Exception("Connection failed"),
            ),
            pytest.raises(DatabaseError, match="Failed to initialize"),
        ):
            async with ClickHouseClient(config):
                pass

    async def test_context_manager_cleanup_on_exception(self, config, mock_session, mock_ch_client):
        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            with pytest.raises(ValueError):  # noqa: PT011, PT012
                async with ClickHouseClient(config):
                    msg = "Test error"
                    raise ValueError(msg)

            mock_session.close.assert_called_once()

    async def test_execute_successful(self, config, mock_session, mock_ch_client):
        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            async with ClickHouseClient(config) as client:
                result = await client.execute("CREATE TABLE test (id UInt32)")
                assert result == "OK"
                mock_ch_client.execute.assert_called_once()

    async def test_execute_not_initialized(self, config):
        client = ClickHouseClient(config)
        with pytest.raises(DatabaseError, match="client is not initialized"):
            await client.execute("SELECT 1")

    async def test_execute_query_fails(self, config, mock_session, mock_ch_client):
        mock_ch_client.execute = AsyncMock(side_effect=Exception("Query error"))

        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            async with ClickHouseClient(config) as client:
                with pytest.raises(DatabaseError, match="Failed to execute query"):
                    await client.execute("SELECT 1")

    async def test_execute_returns_none(self, config, mock_session, mock_ch_client):
        mock_ch_client.execute = AsyncMock(return_value=None)

        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            async with ClickHouseClient(config) as client:
                # aiochclient returns None for successful INSERT/DDL queries, should return empty string
                result = await client.execute("INSERT INTO test VALUES (1)")
                assert result == ""

    async def test_fetch_successful(self, config, mock_session, mock_ch_client):
        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            async with ClickHouseClient(config) as client:
                result = await client.fetch("SELECT * FROM test")
                assert result == [{"id": 1}, {"id": 2}]
                mock_ch_client.fetch.assert_called_once()

    async def test_fetch_not_initialized(self, config):
        client = ClickHouseClient(config)
        with pytest.raises(DatabaseError, match="client is not initialized"):
            await client.fetch("SELECT 1")

    async def test_fetch_query_fails(self, config, mock_session, mock_ch_client):
        mock_ch_client.fetch = AsyncMock(side_effect=Exception("Query error"))

        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            async with ClickHouseClient(config) as client:
                with pytest.raises(DatabaseError, match="Failed to fetch query results"):
                    await client.fetch("SELECT 1")

    async def test_fetch_returns_none(self, config, mock_session, mock_ch_client):
        mock_ch_client.fetch = AsyncMock(return_value=None)

        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            async with ClickHouseClient(config) as client:
                with pytest.raises(DatabaseError, match="Failed to fetch query results"):
                    await client.fetch("SELECT 1")

    async def test_insert_batch_empty_data(self, config, mock_session, mock_ch_client):
        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            async with ClickHouseClient(config) as client:
                await client.insert_batch("test_table", [])
                mock_ch_client.execute.assert_not_called()

    async def test_insert_batch_invalid_table_name(self, config, mock_session, mock_ch_client):
        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            async with ClickHouseClient(config) as client:
                with pytest.raises(DatabaseError, match="Invalid SQL identifier"):
                    await client.insert_batch("invalid-table", [{"id": 1}])

    async def test_insert_batch_single_batch(self, config, mock_session, mock_ch_client):
        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            data = [{"id": 1, "name": "test"}]

            async with ClickHouseClient(config) as client:
                await client.insert_batch("test_table", data)
                mock_ch_client.execute.assert_called_once()

    async def test_insert_batch_multiple_batches(self, config, mock_session, mock_ch_client):
        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            data = [{"id": i, "name": f"test_{i}"} for i in range(5)]

            async with ClickHouseClient(config) as client:
                await client.insert_batch("test_table", data, batch_size=2)
                assert mock_ch_client.execute.call_count == 3

    async def test_insert_batch_uses_default_batch_size(self, config, mock_session, mock_ch_client):
        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            data = [{"id": i} for i in range(1500)]

            async with ClickHouseClient(config) as client:
                await client.insert_batch("test_table", data)
                assert mock_ch_client.execute.call_count == 2

    async def test_insert_batch_invalid_column_name(self, config, mock_session, mock_ch_client):
        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            data = [{"invalid-column": 1}]

            async with ClickHouseClient(config) as client:
                with pytest.raises(DatabaseError, match="Invalid SQL identifier"):
                    await client.insert_batch("test_table", data)

    async def test_insert_batch_execution_fails(self, config, mock_session, mock_ch_client):
        mock_ch_client.execute = AsyncMock(side_effect=Exception("Insert failed"))

        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            data = [{"id": 1}]

            async with ClickHouseClient(config) as client:
                with pytest.raises(DatabaseError, match="Failed to insert batch"):
                    await client.insert_batch("test_table", data)

    async def test_cleanup_closed_session(self, config, mock_session, mock_ch_client):
        mock_session.closed = True

        with (
            patch("shared.infrastructure.database.clickhouse_client.ClientSession") as mock_session_cls,
            patch("shared.infrastructure.database.clickhouse_client.ChClient") as mock_ch_cls,
        ):
            mock_session_cls.return_value = mock_session
            mock_ch_cls.return_value = mock_ch_client

            async with ClickHouseClient(config):
                pass

            mock_session.close.assert_not_called()
