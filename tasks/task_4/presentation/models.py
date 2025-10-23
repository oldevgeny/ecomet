"""Presentation models for Task 4."""

from pydantic import BaseModel, Field


class PhraseViewsResponse(BaseModel):
    """Phrase views response."""

    phrase: str
    views_by_hour: list[tuple[int, int]] = Field(
        description="List of (hour, views_delta) tuples",
    )


class PhraseViewsListResponse(BaseModel):
    """Phrase views list response."""

    campaign_id: int
    total_phrases: int
    results: list[PhraseViewsResponse]
