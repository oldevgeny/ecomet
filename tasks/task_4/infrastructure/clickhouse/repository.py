"""ClickHouse repository implementation for Task 4."""

from loguru import logger

from shared.infrastructure.database.clickhouse_client import ClickHouseClient
from tasks.task_4.domain.entities import PhraseViews
from tasks.task_4.infrastructure.clickhouse.queries import get_phrase_views_by_hour_query


class QueryRepositoryImpl:
    """Query repository implementation."""

    def __init__(self, client: ClickHouseClient) -> None:
        """
        Initialize repository.

        Args:
            client: ClickHouse client
        """
        self._client = client

    async def get_phrase_views_by_hour(self, campaign_id: int) -> list[PhraseViews]:
        """
        Get phrase views by hour for today.

        Args:
            campaign_id: Campaign ID

        Returns:
            List of phrase views
        """
        logger.debug(f"Executing query for campaign {campaign_id}")
        query = get_phrase_views_by_hour_query(campaign_id)
        results = await self._client.fetch(query)

        return [
            PhraseViews(
                phrase=row["phrase"],
                views_by_hour=row["views_by_hour"],
            )
            for row in results
        ]
