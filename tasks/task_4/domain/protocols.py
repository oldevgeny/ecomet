"""Domain protocols for Task 4."""

from typing import Protocol

from tasks.task_4.domain.entities import PhraseViews


class QueryRepository(Protocol):
    """Protocol for query repository."""

    async def get_phrase_views_by_hour(
        self,
        campaign_id: int,
    ) -> list[PhraseViews]:  # pyright: ignore[reportReturnType]
        """Get phrase views by hour for today."""
