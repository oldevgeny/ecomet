"""Integration tests with real PostgreSQL database."""

import asyncio
import os

import pytest
from httpx import ASGITransport, AsyncClient

from tasks.task_1.presentation.app import create_app

pytestmark = pytest.mark.skipif(
    not os.getenv("POSTGRES_DATABASE_URL"),
    reason="PostgreSQL DATABASE_URL not configured",
)


@pytest.mark.anyio
async def test_full_application_lifecycle_with_real_database():
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200

        response = await client.get("/api/db_version")
        assert response.status_code == 200

        data = response.json()
        assert "version" in data
        assert "PostgreSQL" in data["version"]


@pytest.mark.anyio
async def test_concurrent_requests_use_pool_correctly():
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        responses = await asyncio.gather(
            client.get("/api/db_version"),
            client.get("/api/db_version"),
            client.get("/api/db_version"),
            client.get("/api/db_version"),
            client.get("/api/db_version"),
        )

    for response in responses:
        assert response.status_code == 200
        data = response.json()
        assert "PostgreSQL" in data["version"]
