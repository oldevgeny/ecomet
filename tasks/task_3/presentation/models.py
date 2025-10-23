"""Presentation models for Task 3."""

from pydantic import BaseModel, Field


class ScrapeAndSaveRequest(BaseModel):
    """Request model for scrape and save."""

    limit: int = Field(default=100, ge=1, le=100, description="Number of repositories to scrape")


class ScrapeAndSaveResponse(BaseModel):
    """Response model for scrape and save."""

    status: str
    total_repos: int
    total_commits: int
    message: str
