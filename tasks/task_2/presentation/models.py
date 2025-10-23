"""Presentation models for Task 2."""

from pydantic import BaseModel, Field


class RepositoryAuthorCommitsNumResponse(BaseModel):
    """Author commits number response."""

    author: str
    commits_num: int


class RepositoryResponse(BaseModel):
    """Repository response model."""

    name: str
    owner: str
    position: int
    stars: int
    watchers: int
    forks: int
    language: str | None
    authors_commits_num_today: list[RepositoryAuthorCommitsNumResponse]


class RepositoriesResponse(BaseModel):
    """Repositories list response."""

    total: int
    repositories: list[RepositoryResponse]


class RepositoriesRequest(BaseModel):
    """Repositories request parameters."""

    limit: int = Field(default=100, ge=1, le=100, description="Number of repositories to fetch")
