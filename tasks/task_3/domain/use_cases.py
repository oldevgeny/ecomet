"""Use cases for Task 3."""

from datetime import UTC, datetime

from loguru import logger

from shared.infrastructure.config.clickhouse import ClickHouseConfig
from shared.infrastructure.database.clickhouse_client import ClickHouseClient
from tasks.task_2.domain.entities import Repository
from tasks.task_2.domain.protocols import Scraper


class ScrapAndSaveUseCase:
    """Use case for scraping repositories and saving to ClickHouse."""

    def __init__(self, scraper: Scraper, clickhouse_config: ClickHouseConfig) -> None:
        """
        Initialize use case.

        Args:
            scraper: GitHub scraper
            clickhouse_config: ClickHouse configuration
        """
        self._scraper = scraper
        self._clickhouse_config = clickhouse_config

    async def execute(self, limit: int = 100) -> dict[str, int]:
        """
        Execute scraping and saving.

        Args:
            limit: Number of repositories to scrape

        Returns:
            Statistics about saved data
        """
        logger.info(f"Starting scrape and save for {limit} repositories")

        # 1. Scrape repositories
        repositories = await self._scraper.get_repositories(limit)
        logger.info(f"Scraped {len(repositories)} repositories")

        # 2. Save to ClickHouse
        async with ClickHouseClient(self._clickhouse_config) as client:
            await self._save_repositories(client, repositories)
            await self._save_positions(client, repositories)
            await self._save_commits(client, repositories)

        logger.info("Successfully saved all data to ClickHouse")

        return {
            "total_repos": len(repositories),
            "total_commits": sum(len(repo.authors_commits_num_today) for repo in repositories),
        }

    async def _save_repositories(
        self,
        client: ClickHouseClient,
        repositories: list[Repository],
    ) -> None:
        """Save repositories to ClickHouse using batch insertion."""
        # ClickHouse DateTime has second precision, remove microseconds
        now = datetime.now(tz=UTC).replace(microsecond=0)
        data = [
            {
                "name": repo.name,
                "owner": repo.owner,
                "stars": repo.stars,
                "watchers": repo.watchers,
                "forks": repo.forks,
                "language": repo.language or "",
                "updated": now,
            }
            for repo in repositories
        ]

        logger.info(f"Saving {len(data)} repositories using batch insertion")
        await client.insert_batch("repositories", data)

    async def _save_positions(
        self,
        client: ClickHouseClient,
        repositories: list[Repository],
    ) -> None:
        """Save repository positions to ClickHouse using batch insertion."""
        data = [
            {
                "date": datetime.now(tz=UTC).date(),
                "repo": f"{repo.owner}/{repo.name}",
                "position": repo.position,
            }
            for repo in repositories
        ]

        logger.info(f"Saving {len(data)} positions using batch insertion")
        await client.insert_batch("repositories_positions", data)

    async def _save_commits(
        self,
        client: ClickHouseClient,
        repositories: list[Repository],
    ) -> None:
        """Save author commits to ClickHouse using batch insertion."""
        data = []
        for repo in repositories:
            for author_commits in repo.authors_commits_num_today:
                data.append(
                    {
                        "date": datetime.now(tz=UTC).date(),
                        "repo": f"{repo.owner}/{repo.name}",
                        "author": author_commits.author,
                        "commits_num": author_commits.commits_num,
                    }
                )

        if data:
            logger.info(f"Saving {len(data)} author commits using batch insertion")
            await client.insert_batch("repositories_authors_commits", data)
