"""Tests for configuration."""

import pytest
from pydantic import ValidationError

from shared.infrastructure.config.clickhouse import ClickHouseConfig
from shared.infrastructure.config.github import GitHubConfig
from shared.infrastructure.config.postgres import PostgresConfig


def test_postgres_config_with_valid_url():
    config = PostgresConfig(
        database_url="postgresql://user:pass@localhost:5432/testdb",
    )

    assert config.min_pool_size == 10
    assert config.max_pool_size == 20


def test_postgres_config_validates_pool_size():
    with pytest.raises(ValidationError):
        PostgresConfig(
            database_url="postgresql://user:pass@localhost:5432/testdb",
            min_pool_size=0,
        )


def test_clickhouse_config_defaults(monkeypatch):
    monkeypatch.delenv("CLICKHOUSE_HOST", raising=False)
    monkeypatch.delenv("CLICKHOUSE_PORT", raising=False)
    monkeypatch.delenv("CLICKHOUSE_DATABASE", raising=False)
    monkeypatch.delenv("CLICKHOUSE_BATCH_SIZE", raising=False)

    config = ClickHouseConfig(_env_file=None)

    assert config.host == "localhost"
    assert config.port == 9000
    assert config.database == "test"
    assert config.batch_size == 1000


def test_clickhouse_config_validates_port():
    with pytest.raises(ValidationError):
        ClickHouseConfig(port=99999)


def test_github_config_requires_access_token(monkeypatch):
    monkeypatch.delenv("GITHUB_ACCESS_TOKEN", raising=False)

    with pytest.raises(ValidationError):
        GitHubConfig(_env_file=None)


def test_github_config_with_token():
    config = GitHubConfig(access_token="ghp_test_token")

    assert config.max_concurrent_requests == 10
    assert config.requests_per_second == 5
    assert config.api_base_url == "https://api.github.com"
