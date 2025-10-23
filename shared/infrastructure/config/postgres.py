"""PostgreSQL configuration."""

from pydantic import Field, PostgresDsn
from pydantic_settings import SettingsConfigDict

from shared.infrastructure.config.base import BaseConfig


class PostgresConfig(BaseConfig):
    """PostgreSQL database configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="POSTGRES_",
    )

    # Database URL
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection URL",
    )

    # Pool settings
    min_pool_size: int = Field(default=10, ge=1, description="Minimum pool size")
    max_pool_size: int = Field(default=20, ge=1, description="Maximum pool size")
    max_queries: int = Field(default=50000, ge=1, description="Max queries per connection")
    max_inactive_connection_lifetime: float = Field(
        default=300.0,
        ge=0,
        description="Max inactive connection lifetime in seconds",
    )
    timeout: float = Field(default=60.0, ge=0, description="Connection timeout in seconds")
