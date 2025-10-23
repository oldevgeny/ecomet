"""API endpoints for Task 2."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from loguru import logger

from tasks.task_2.infrastructure.github_scraper import GithubReposScrapper
from tasks.task_2.presentation.dependencies import get_scraper
from tasks.task_2.presentation.models import (
    RepositoriesResponse,
    RepositoryAuthorCommitsNumResponse,
    RepositoryResponse,
)

router = APIRouter(prefix="/api", tags=["repositories"])


@router.get("/repositories", response_model=RepositoriesResponse)
async def get_repositories(
    scraper: Annotated[GithubReposScrapper, Depends(get_scraper)],
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> RepositoriesResponse:
    """
    Get top GitHub repositories with commit statistics.

    Args:
        scraper: GitHub scraper instance
        limit: Number of repositories to fetch (1-100)

    Returns:
        List of repositories with commit statistics
    """
    logger.info(f"Fetching {limit} repositories")

    repositories = await scraper.get_repositories(limit)

    return RepositoriesResponse(
        total=len(repositories),
        repositories=[
            RepositoryResponse(
                name=repo.name,
                owner=repo.owner,
                position=repo.position,
                stars=repo.stars,
                watchers=repo.watchers,
                forks=repo.forks,
                language=repo.language,
                authors_commits_num_today=[
                    RepositoryAuthorCommitsNumResponse(
                        author=author.author,
                        commits_num=author.commits_num,
                    )
                    for author in repo.authors_commits_num_today
                ],
            )
            for repo in repositories
        ],
    )
