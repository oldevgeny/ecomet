"""ClickHouse configuration."""

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from shared.infrastructure.config.base import BaseConfig


class ClickHouseConfig(BaseConfig):
    """ClickHouse database configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CLICKHOUSE_",
    )

    host: str = Field(default="localhost", description="ClickHouse host")
    port: int = Field(default=9000, ge=1, le=65535, description="ClickHouse port")
    database: str = Field(default="test", description="Database name")
    user: str = Field(default="default", description="Username")
    password: str = Field(default="", description="Password")

    # Batch settings
    batch_size: int = Field(default=1000, ge=1, description="Batch size for bulk inserts")
    max_retries: int = Field(default=3, ge=0, description="Max retries for failed operations")
