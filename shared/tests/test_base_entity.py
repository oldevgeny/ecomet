"""Tests for base domain entity."""

import pytest
from pydantic import ValidationError

from shared.domain.entities.base import DomainEntity


def test_domain_entity_is_frozen() -> None:
    class TestEntity(DomainEntity):
        name: str
        value: int

    entity = TestEntity(name="test", value=42)

    with pytest.raises(ValidationError):
        entity.name = "changed"


def test_domain_entity_strict_mode() -> None:
    class TestEntity(DomainEntity):
        name: str
        value: int

    with pytest.raises(ValidationError):
        TestEntity(name="test", value="not an int")  # type: ignore[arg-type]


def test_domain_entity_creation() -> None:
    class TestEntity(DomainEntity):
        name: str
        value: int

    entity = TestEntity(name="test", value=42)

    assert entity.name == "test"
    assert entity.value == 42
