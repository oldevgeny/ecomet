"""Domain entities for Task 4."""

from shared.domain.entities.base import DomainEntity


class PhraseViews(DomainEntity):
    """Phrase views by hour."""

    phrase: str
    views_by_hour: list[tuple[int, int]]
