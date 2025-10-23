"""API endpoints for Task 4."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from loguru import logger

from tasks.task_4.domain.use_cases import GetPhraseViewsUseCase
from tasks.task_4.presentation.dependencies import get_use_case
from tasks.task_4.presentation.models import PhraseViewsListResponse, PhraseViewsResponse

router = APIRouter(prefix="/api", tags=["phrase-views"])


@router.get("/phrase-views", response_model=PhraseViewsListResponse)
async def get_phrase_views(
    use_case: Annotated[GetPhraseViewsUseCase, Depends(get_use_case)],
    campaign_id: Annotated[int, Query(ge=1)],
) -> PhraseViewsListResponse:
    """
    Get phrase views by hour for today.

    Args:
        use_case: GetPhraseViewsUseCase instance
        campaign_id: Campaign ID

    Returns:
        Phrase views by hour
    """
    logger.info(f"Getting phrase views for campaign {campaign_id}")

    phrase_views = await use_case.execute(campaign_id)

    return PhraseViewsListResponse(
        campaign_id=campaign_id,
        total_phrases=len(phrase_views),
        results=[
            PhraseViewsResponse(
                phrase=pv.phrase,
                views_by_hour=pv.views_by_hour,
            )
            for pv in phrase_views
        ],
    )
