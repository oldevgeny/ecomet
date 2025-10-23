"""GitHub repositories scraper implementation."""

import asyncio
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from loguru import logger

from shared.domain.entities.exceptions import ScraperError
from tasks.task_2.domain.entities import Repository, RepositoryAuthorCommitsNum
from tasks.task_2.domain.protocols import HTTPClient


class GithubReposScrapper:
    """GitHub repositories scraper with rate limiting."""

    def __init__(self, client: HTTPClient, top_limit: int = 100) -> None:
        """
        Initialize GitHub scraper.

        Args:
            client: HTTP client with rate limiting
            top_limit: Maximum number of top repositories to fetch
        """
        self._client = client
        self._top_limit = top_limit
        self._base_url = "https://api.github.com"

    async def get_repositories(self, limit: int) -> list[Repository]:
        """
        Get top repositories with commit statistics.

        Args:
            limit: Number of repositories to fetch

        Returns:
            List of repositories with commit statistics

        Raises:
            ScraperError: If scraping fails
        """
        try:
            logger.info(f"Fetching top {limit} repositories")
            top_repos = await self._get_top_repositories(limit)
            logger.info(f"Fetched {len(top_repos)} repositories")

            repositories = await self._process_repositories_with_commits(top_repos)
            logger.info(f"Successfully processed {len(repositories)}/{len(top_repos)} repositories")
        except Exception as exc:
            error_msg = f"Failed to scrape repositories: {exc}"
            logger.error(error_msg)
            raise ScraperError(error_msg) from exc
        else:
            return repositories

    async def _process_repositories_with_commits(
        self,
        top_repos: list[dict],
    ) -> list[Repository]:
        """
        Process repositories with commits concurrently.

        Args:
            top_repos: List of top repositories data

        Returns:
            List of successfully processed repositories
        """
        tasks = [self._get_repository_with_commits(repo, position) for position, repo in enumerate(top_repos, start=1)]
        repositories = await asyncio.gather(*tasks, return_exceptions=True)
        return self._filter_successful_repositories(repositories)

    def _filter_successful_repositories(
        self,
        repositories: list[Repository | BaseException],
    ) -> list[Repository]:
        """
        Filter out failed repositories and log warnings.

        Args:
            repositories: List of repositories or exceptions

        Returns:
            List of successfully processed repositories
        """
        successful_repositories = []
        for idx, repo in enumerate(repositories):
            if isinstance(repo, BaseException):
                logger.warning(f"Failed to process repository at position {idx + 1}: {repo}")
            else:
                successful_repositories.append(repo)
        return successful_repositories

    async def _get_top_repositories(self, limit: int) -> list[dict]:
        """
        Get top repositories from GitHub.

        Args:
            limit: Number of repositories to fetch

        Returns:
            List of repository data
        """
        url = f"{self._base_url}/search/repositories"
        params = {
            "q": "stars:>1",
            "sort": "stars",
            "order": "desc",
            "per_page": min(limit, 100),
        }

        data = await self._client.get(url, params=params)
        return data.get("items", [])

    async def _get_repository_with_commits(
        self,
        repo_data: dict,
        position: int,
    ) -> Repository:
        """
        Get repository with today's commit statistics.

        Args:
            repo_data: Repository data from GitHub API
            position: Position in top repositories

        Returns:
            Repository with commit statistics
        """
        owner = repo_data["owner"]["login"]
        name = repo_data["name"]

        logger.debug(f"Fetching commits for {owner}/{name}")
        commits = await self._get_repository_commits(owner, name)

        # Group commits by author
        author_commits = self._group_commits_by_author(commits)

        return Repository(
            name=name,
            owner=owner,
            position=position,
            stars=repo_data["stargazers_count"],
            watchers=repo_data["watchers_count"],
            forks=repo_data["forks_count"],
            language=repo_data.get("language"),
            authors_commits_num_today=author_commits,
        )

    async def _get_repository_commits(self, owner: str, name: str) -> list[dict]:
        """
        Get repository commits for the last day.

        Args:
            owner: Repository owner
            name: Repository name

        Returns:
            List of commits
        """
        url = f"{self._base_url}/repos/{owner}/{name}/commits"

        # Get commits since yesterday
        since = (datetime.now(tz=UTC) - timedelta(days=1)).isoformat()
        params = {
            "since": since,
            "per_page": 100,
        }

        try:
            data = await self._client.get(url, params=params)
            return data if isinstance(data, list) else []
        except ScraperError as exc:
            logger.warning(f"Failed to fetch commits for {owner}/{name}: {exc}")
            return []

    def _group_commits_by_author(self, commits: list[dict]) -> list[RepositoryAuthorCommitsNum]:
        """
        Group commits by author and count.

        Args:
            commits: List of commit data

        Returns:
            List of author commit counts
        """
        author_counts: dict[str, int] = defaultdict(int)

        for commit in commits:
            author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
            author_counts[author] += 1

        return [
            RepositoryAuthorCommitsNum(author=author, commits_num=count)
            for author, count in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
        ]
