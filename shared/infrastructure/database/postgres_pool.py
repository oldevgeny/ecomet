"""PostgreSQL connection pool implementation."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
from loguru import logger

from shared.domain.entities.exceptions import DatabaseError
from shared.infrastructure.config.postgres import PostgresConfig


class PostgreSQLPool:
    """PostgreSQL connection pool manager."""

    def __init__(self, config: PostgresConfig) -> None:
        """
        Initialize PostgreSQL pool manager.

        Args:
            config: PostgreSQL configuration
        """
        self._config = config
        self._pool: asyncpg.Pool | None = None

    async def create_pool(self) -> None:
        """Create and initialize connection pool."""
        try:
            logger.info("Creating PostgreSQL connection pool")
            self._pool = await asyncpg.create_pool(
                dsn=str(self._config.database_url),
                min_size=self._config.min_pool_size,
                max_size=self._config.max_pool_size,
                max_queries=self._config.max_queries,
                max_inactive_connection_lifetime=self._config.max_inactive_connection_lifetime,
                timeout=self._config.timeout,
            )
            logger.info("PostgreSQL connection pool created successfully")
        except Exception as exc:
            error_msg = f"Failed to create PostgreSQL pool: {exc}"
            logger.error(error_msg)
            raise DatabaseError(error_msg) from exc

    async def close_pool(self) -> None:
        """Close the connection pool."""
        if self._pool:
            logger.info("Closing PostgreSQL connection pool")
            await self._pool.close()
            logger.info("PostgreSQL connection pool closed")

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[asyncpg.Connection]:
        """
        Acquire a connection from the pool.

        Yields:
            Database connection

        Raises:
            DatabaseError: If pool is not initialized or connection fails
        """
        if not self._pool:
            msg = "Connection pool is not initialized"
            raise DatabaseError(msg)

        try:
            async with self._pool.acquire() as connection:
                yield connection
        except Exception as exc:
            error_msg = f"Failed to acquire database connection: {exc}"
            logger.error(error_msg)
            raise DatabaseError(error_msg) from exc

    @property
    def pool(self) -> asyncpg.Pool:
        """
        Get the underlying pool.

        Returns:
            Connection pool

        Raises:
            DatabaseError: If pool is not initialized
        """
        if not self._pool:
            msg = "Connection pool is not initialized"
            raise DatabaseError(msg)
        return self._pool
