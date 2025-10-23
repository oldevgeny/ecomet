"""GitHub API configuration."""

from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from shared.infrastructure.config.base import BaseConfig


class GitHubConfig(BaseConfig):
    """GitHub API configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GITHUB_",
    )

    access_token: SecretStr = Field(..., description="GitHub personal access token")
    api_base_url: str = Field(
        default="https://api.github.com",
        description="GitHub API base URL",
    )

    # Rate limiting
    max_concurrent_requests: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum concurrent requests",
    )
    requests_per_second: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Requests per second limit",
    )

    # Repository settings
    top_repositories_limit: int = Field(
        default=100,
        ge=1,
        le=100,
        description="Number of top repositories to fetch",
    )

    # Timeout settings
    request_timeout: float = Field(
        default=30.0,
        ge=1.0,
        description="Request timeout in seconds",
    )
