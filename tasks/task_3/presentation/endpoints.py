"""API endpoints for Task 3."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from loguru import logger

from tasks.task_3.domain.use_cases import ScrapAndSaveUseCase
from tasks.task_3.presentation.dependencies import get_use_case
from tasks.task_3.presentation.models import ScrapeAndSaveResponse

router = APIRouter(prefix="/api", tags=["scrape"])


@router.post("/scrape-and-save", response_model=ScrapeAndSaveResponse)
async def scrape_and_save(
    use_case: Annotated[ScrapAndSaveUseCase, Depends(get_use_case)],
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> ScrapeAndSaveResponse:
    """
    Scrape GitHub repositories and save to ClickHouse.

    Args:
        use_case: ScrapAndSaveUseCase instance
        limit: Number of repositories to scrape (1-100)

    Returns:
        Operation result
    """
    logger.info(f"Starting scrape and save for {limit} repositories")

    result = await use_case.execute(limit=limit)

    return ScrapeAndSaveResponse(
        status="success",
        total_repos=result["total_repos"],
        total_commits=result["total_commits"],
        message=f"Successfully scraped and saved {result['total_repos']} repositories",
    )
