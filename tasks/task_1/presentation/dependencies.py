"""FastAPI dependencies for Task 1."""

from collections.abc import AsyncIterator
from typing import Annotated

import asyncpg
from fastapi import Depends, Request
from loguru import logger

from shared.domain.entities.exceptions import DatabaseError
from shared.infrastructure.database.postgres_pool import PostgreSQLPool


def get_pool(request: Request) -> PostgreSQLPool:
    """
    Get PostgreSQL pool from app state.

    Args:
        request: FastAPI request object

    Returns:
        PostgreSQL pool instance

    Raises:
        DatabaseError: If pool is not initialized
    """
    pool = getattr(request.app.state, "pool", None)
    if pool is None:
        msg = "PostgreSQL pool is not initialized"
        raise DatabaseError(msg)
    return pool


async def get_pg_connection(
    pool: Annotated[PostgreSQLPool, Depends(get_pool)],
) -> AsyncIterator[asyncpg.Connection]:
    """
    Dependency to get PostgreSQL connection from pool.

    Args:
        pool: PostgreSQL pool instance

    Yields:
        Database connection

    Raises:
        DatabaseError: If connection acquisition fails
    """
    logger.debug("Acquiring PostgreSQL connection from pool")
    async with pool.acquire() as connection:
        logger.debug("PostgreSQL connection acquired")
        yield connection
    logger.debug("PostgreSQL connection released")
