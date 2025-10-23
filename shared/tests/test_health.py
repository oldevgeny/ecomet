"""Tests for health check router."""

import pytest
from httpx import ASGITransport, AsyncClient

from shared.presentation.fastapi.health import create_health_router


@pytest.fixture
def health_app():
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(create_health_router(version="1.2.3"))
    return app


@pytest.mark.anyio
async def test_health_check_endpoint(health_app) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=health_app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.2.3"
