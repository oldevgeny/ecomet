"""Repository protocols for data access."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

EntityT = TypeVar("EntityT")


class Repository[EntityT](ABC):
    """Base repository protocol."""

    @abstractmethod
    async def save(self, entity: EntityT) -> None:
        """Save an entity."""

    @abstractmethod
    async def save_many(self, entities: list[EntityT]) -> None:
        """Save multiple entities."""


class QueryRepository(ABC):
    """Repository for executing queries."""

    @abstractmethod
    async def execute_query(self, query: str, params: dict[str, Any]) -> list[Any]:
        """Execute a query and return results."""
