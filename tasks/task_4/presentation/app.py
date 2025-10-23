"""FastAPI application for Task 4."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from loguru import logger

from shared.infrastructure.config.clickhouse import ClickHouseConfig
from shared.infrastructure.database.clickhouse_client import ClickHouseClient
from shared.infrastructure.logging.setup import setup_logging
from shared.infrastructure.version import get_version_from_pyproject
from shared.presentation.fastapi.exception_handlers import register_exception_handlers
from shared.presentation.fastapi.health import create_health_router
from tasks.task_4.domain.use_cases import GetPhraseViewsUseCase
from tasks.task_4.infrastructure.clickhouse.repository import QueryRepositoryImpl
from tasks.task_4.presentation.endpoints import router

TASK_ROOT = Path(__file__).parent.parent
VERSION = get_version_from_pyproject(TASK_ROOT / "pyproject.toml")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan manager.

    Args:
        app: FastAPI application

    Yields:
        None
    """
    logger.info("Starting Task 4 application")

    # Initialize ClickHouse client and repository
    config = ClickHouseConfig()
    client = ClickHouseClient(config)
    await client.__aenter__()

    repository = QueryRepositoryImpl(client)
    use_case = GetPhraseViewsUseCase(repository)

    app.state.client = client
    app.state.repository = repository
    app.state.use_case = use_case

    logger.info("Task 4 application initialized")

    yield

    # Cleanup
    await client.__aexit__(None, None, None)
    logger.info("Task 4 application shutdown complete")


def create_app() -> FastAPI:
    """
    Create FastAPI application.

    Returns:
        FastAPI application instance
    """
    setup_logging()

    app = FastAPI(
        title="E-Comet Task 4",
        version=VERSION,
        description="ClickHouse queries for phrase views",
        lifespan=lifespan,
    )

    # Register routers
    app.include_router(router=create_health_router(version=VERSION))
    app.include_router(router=router)

    # Register exception handlers
    register_exception_handlers(app)

    return app
