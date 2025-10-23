"""ClickHouse client implementation."""

import re
from types import TracebackType
from typing import Any

from aiochclient import ChClient
from aiohttp import ClientSession, TCPConnector
from loguru import logger

from shared.domain.entities.exceptions import DatabaseError
from shared.infrastructure.config.clickhouse import ClickHouseConfig

VALID_IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
VALID_QUALIFIED_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$")


def validate_sql_identifier(identifier: str, allow_qualified: bool = False) -> None:
    """
    Validate SQL identifier (table or column name).

    Args:
        identifier: SQL identifier to validate
        allow_qualified: Allow qualified names like 'database.table'

    Raises:
        DatabaseError: If identifier is invalid
    """
    pattern = VALID_QUALIFIED_NAME_PATTERN if allow_qualified else VALID_IDENTIFIER_PATTERN
    if not pattern.match(identifier):
        msg = f"Invalid SQL identifier: {identifier}"
        raise DatabaseError(msg)


class ClickHouseClient:
    """ClickHouse client with context manager support."""

    def __init__(self, config: ClickHouseConfig) -> None:
        """
        Initialize ClickHouse client.

        Args:
            config: ClickHouse configuration
        """
        self._config = config
        self._session: ClientSession | None = None
        self._client: ChClient | None = None

    async def __aenter__(self) -> "ClickHouseClient":
        """
        Enter context manager - create client connection.

        Returns:
            Self instance
        """
        logger.info("Initializing ClickHouse client")
        try:
            connector = TCPConnector(limit=100)
            self._session = ClientSession(connector=connector)

            url = f"http://{self._config.host}:{self._config.port}"
            self._client = ChClient(
                session=self._session,
                url=url,
                user=self._config.user,
                password=self._config.password,
                database=self._config.database,
            )

            logger.info("ClickHouse client initialized successfully")
        except Exception as exc:
            error_msg = f"Failed to initialize ClickHouse client: {exc}"
            logger.error(error_msg)
            raise DatabaseError(error_msg) from exc
        else:
            return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """
        Exit context manager - close client connection.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        await self._cleanup()
        if exc_val:
            logger.error(f"ClickHouse client error: {exc_val}")

    async def _cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Closing ClickHouse client")
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info("ClickHouse client closed")

    async def execute(self, query: str, *args: Any) -> str:  # noqa: ANN401
        """
        Execute a query without returning results.

        Args:
            query: SQL query
            *args: Query parameters

        Returns:
            Query result status

        Raises:
            DatabaseError: If client is not initialized or query fails
        """
        if not self._client:
            msg = "ClickHouse client is not initialized"
            raise DatabaseError(msg)

        try:
            logger.debug(f"Executing query: {query[:100]}...")
            result = await self._client.execute(query, *args)
        except Exception as exc:
            error_msg = f"Failed to execute query: {exc}"
            logger.error(error_msg)
            raise DatabaseError(error_msg) from exc
        else:
            logger.debug("Query executed successfully")
            # aiochclient returns empty string or None for successful INSERT/DDL queries
            return "" if result is None else result

    async def fetch(self, query: str, *args: Any) -> list[Any]:  # noqa: ANN401
        """
        Fetch query results.

        Args:
            query: SQL query
            *args: Query parameters

        Returns:
            Query results

        Raises:
            DatabaseError: If client is not initialized or query fails
        """
        if not self._client:
            msg = "ClickHouse client is not initialized"
            raise DatabaseError(msg)

        try:
            logger.debug(f"Fetching query: {query[:100]}...")
            result = await self._client.fetch(query, *args)
            logger.debug(f"Fetched {len(result)} rows")
        except Exception as exc:
            error_msg = f"Failed to fetch query results: {exc}"
            logger.error(error_msg)
            raise DatabaseError(error_msg) from exc
        else:
            if result is None:
                msg = "Query result is None"
                raise DatabaseError(msg)
            return result

    async def _insert_single_batch(
        self,
        table: str,
        batch: list[dict[str, Any]],
        columns: list[str],
    ) -> None:
        """Insert a single batch of rows."""
        if not self._client:
            msg = "ClickHouse client is not initialized"
            raise DatabaseError(msg)

        rows = [tuple(row_dict[col] for col in columns) for row_dict in batch]
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES"
        await self._client.execute(query, *rows)

    async def _process_batches(
        self,
        table: str,
        data: list[dict[str, Any]],
        columns: list[str],
        batch_size: int,
    ) -> None:
        """Process and insert data in batches."""
        total_rows = len(data)
        for batch_start in range(0, total_rows, batch_size):
            batch_end = min(batch_start + batch_size, total_rows)
            batch = data[batch_start:batch_end]

            if batch:
                await self._insert_single_batch(table, batch, columns)
                batch_number = batch_start // batch_size + 1
                logger.debug(
                    f"Inserted batch {batch_number}: {len(batch)} rows ({batch_start + 1}-{batch_end})",
                )

    async def insert_batch(
        self,
        table: str,
        data: list[dict[str, Any]],
        batch_size: int | None = None,
    ) -> None:
        """
        Insert data in batches using aiochclient's native batch insert.

        Args:
            table: Table name
            data: List of dictionaries representing rows
            batch_size: Batch size (uses config default if not provided)

        Raises:
            DatabaseError: If client is not initialized or insert fails
        """
        if not data:
            logger.warning("No data to insert")
            return

        if not self._client:
            msg = "ClickHouse client is not initialized"
            raise DatabaseError(msg)

        validate_sql_identifier(table, allow_qualified=True)

        effective_batch_size = batch_size or self._config.batch_size
        total_rows = len(data)
        logger.info(f"Inserting {total_rows} rows into {table} (batch_size={effective_batch_size})")

        try:
            columns = list(data[0].keys())
            for column_name in columns:
                validate_sql_identifier(column_name)
            await self._process_batches(table, data, columns, effective_batch_size)
            logger.info(f"Successfully inserted {total_rows} rows into {table}")
        except Exception as exc:
            error_msg = f"Failed to insert batch into {table}: {exc}"
            logger.error(error_msg)
            raise DatabaseError(error_msg) from exc
