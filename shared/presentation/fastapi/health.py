"""Health check endpoint."""

from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str


def create_health_router(version: str) -> APIRouter:
    """
    Create health check router.

    Args:
        version: Application version

    Returns:
        FastAPI router with health endpoint
    """
    router = APIRouter(tags=["health"])

    @router.get(
        "/health",
        response_model=HealthResponse,
        status_code=status.HTTP_200_OK,
        summary="Health check",
        description="Check if the service is healthy",
    )
    async def health_check() -> dict[str, Any]:
        """Health check endpoint."""
        return {"status": "healthy", "version": version}

    return router
