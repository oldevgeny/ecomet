"""Domain entities for Task 2."""

from shared.domain.entities.base import DomainEntity


class RepositoryAuthorCommitsNum(DomainEntity):
    """Repository author commits number."""

    author: str
    commits_num: int


class Repository(DomainEntity):
    """GitHub repository with commit statistics."""

    name: str
    owner: str
    position: int
    stars: int
    watchers: int
    forks: int
    language: str | None
    authors_commits_num_today: list[RepositoryAuthorCommitsNum]
