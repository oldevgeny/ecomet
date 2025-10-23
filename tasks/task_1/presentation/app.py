"""FastAPI application factory for Task 1."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from loguru import logger

from shared.infrastructure.config.postgres import PostgresConfig
from shared.infrastructure.database.postgres_pool import PostgreSQLPool
from shared.infrastructure.logging.setup import setup_logging
from shared.infrastructure.version import get_version_from_pyproject
from shared.presentation.fastapi.exception_handlers import register_exception_handlers
from shared.presentation.fastapi.health import create_health_router
from tasks.task_1.presentation.endpoints import create_router

TASK_ROOT = Path(__file__).parent.parent
VERSION = get_version_from_pyproject(TASK_ROOT / "pyproject.toml")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting Task 1 application")

    config = PostgresConfig()
    logger.info("Configuration loaded")

    pool = PostgreSQLPool(config)
    await pool.create_pool()

    app.state.pool = pool

    logger.info("Task 1 application started successfully")

    yield

    logger.info("Shutting down Task 1 application")
    await pool.close_pool()
    logger.info("Task 1 application shut down successfully")


def create_app() -> FastAPI:
    setup_logging(log_level="INFO")

    app = FastAPI(
        title="E-Comet Task 1",
        description="PostgreSQL Connection Pool with Clean Architecture",
        version=VERSION,
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    app.include_router(create_health_router(version=VERSION))
    app.include_router(create_router())

    logger.info("FastAPI application created")
    return app
