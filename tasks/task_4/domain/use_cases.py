"""Use cases for Task 4."""

from loguru import logger

from tasks.task_4.domain.entities import PhraseViews
from tasks.task_4.domain.protocols import QueryRepository


class GetPhraseViewsUseCase:
    """Use case for getting phrase views by hour."""

    def __init__(self, repository: QueryRepository) -> None:
        """
        Initialize use case.

        Args:
            repository: Query repository
        """
        self._repository = repository

    async def execute(self, campaign_id: int) -> list[PhraseViews]:
        """
        Execute getting phrase views.

        Args:
            campaign_id: Campaign ID

        Returns:
            List of phrase views by hour
        """
        logger.info(f"Fetching phrase views for campaign {campaign_id}")

        results = await self._repository.get_phrase_views_by_hour(campaign_id)

        logger.info(f"Found {len(results)} phrases with views")
        return results
