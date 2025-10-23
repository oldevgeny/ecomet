"""API endpoints for Task 1."""

from typing import Annotated

import asyncpg
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from tasks.task_1.presentation.dependencies import get_pg_connection


class DBVersionResponse(BaseModel):
    version: str


def create_router() -> APIRouter:
    router = APIRouter(prefix="/api", tags=["database"])

    @router.get(
        "/db_version",
        response_model=DBVersionResponse,
        status_code=status.HTTP_200_OK,
        summary="Get database version",
        description="Retrieve PostgreSQL database version",
    )
    async def get_db_version(
        conn: Annotated[asyncpg.Connection, Depends(get_pg_connection)],
    ) -> DBVersionResponse:
        version: str = await conn.fetchval("SELECT version()")
        return DBVersionResponse(version=version)

    return router
