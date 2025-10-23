"""Database protocols for dependency inversion."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class DatabaseConnection(Protocol):
    """Protocol for database connection."""

    async def fetchval(self, query: str, *args: Any) -> Any:  # noqa: ANN401
        """Fetch a single value from database."""

    async def fetch(self, query: str, *args: Any) -> list[Any]:  # noqa: ANN401  # pyright: ignore[reportReturnType]
        """Fetch multiple rows from database."""

    async def execute(self, query: str, *args: Any) -> str:  # noqa: ANN401  # pyright: ignore[reportReturnType]
        """Execute a query without returning results."""


@runtime_checkable
class DatabasePool(Protocol):
    """Protocol for database connection pool."""

    def acquire(self) -> Any:  # noqa: ANN401
        """Acquire a connection from the pool."""

    async def close(self) -> None:
        """Close the connection pool."""
