"""Base domain entity."""

from pydantic import BaseModel, ConfigDict


class DomainEntity(BaseModel):
    """Base class for all domain entities."""

    model_config = ConfigDict(frozen=True, strict=True)
