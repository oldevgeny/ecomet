"""Domain protocols for Task 2."""

from typing import Any, Protocol

from tasks.task_2.domain.entities import Repository


class HTTPClient(Protocol):
    """Protocol for HTTP client."""

    async def get(self, url: str, **kwargs: Any) -> dict[str, Any]:  # noqa: ANN401
        """Make GET request."""
        ...

    async def close(self) -> None:
        """Close client."""
        ...


class Scraper(Protocol):
    """Protocol for GitHub scraper."""

    async def get_repositories(self, limit: int) -> list[Repository]:
        """Get top repositories with commit statistics."""
        ...
