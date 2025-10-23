# Task 1: PostgreSQL Connection Pool

## Overview

Implementation of PostgreSQL connection pool using Clean Architecture principles. This task demonstrates proper pool management with FastAPI lifespan, dependency injection, and no global variables.

## Requirements Met

✅ **Requirement 1.a**: No global variables - uses `app.state` for pool storage
✅ **Requirement 1.b**: Uses asyncpg connection pool
✅ **Requirement 1.c**: No deprecated FastAPI features - uses modern `lifespan` context manager

## Architecture

```
task_1/
├── presentation/
│   ├── dependencies.py  # DI for pool and connections
│   ├── endpoints.py     # API routes
│   └── app.py          # FastAPI app factory
├── tests/
│   ├── unit/           # Unit tests with mocks
│   └── integration/    # Integration tests with real DB
└── main.py             # Entry point
```

## Configuration

Create `.env` file (see `.env.example`):

```env
POSTGRES_DATABASE_URL=postgresql://user:password@localhost:5432/dbname
POSTGRES_MIN_POOL_SIZE=10
POSTGRES_MAX_POOL_SIZE=20
```

## Running

### Locally

```bash
# Install dependencies
uv sync

# Set environment variables
export POSTGRES_DATABASE_URL=postgresql://ecomet:ecomet@localhost:5432/ecomet

# Run application
uv run uvicorn tasks.task_1.presentation.app:create_app --factory --reload --port 8001
```

### With Docker

```bash
docker compose up task_1
```

## API Endpoints

### Health Check

```bash
curl http://localhost:8001/health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Get Database Version

```bash
curl http://localhost:8001/api/db_version
```

Response:
```json
{
  "version": "PostgreSQL 16.0 ..."
}
```

## Testing

```bash
# Run all tests
uv run pytest tasks/task_1/tests/

# Run only unit tests
uv run pytest tasks/task_1/tests/unit/

# Run with coverage
uv run pytest tasks/task_1/tests/ --cov=tasks.task_1 --cov-report=term-missing
```

## Key Implementation Details

### No Global Variables

The pool is stored in `app.state.pool` (FastAPI's recommended approach):

```python
# app.py
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    pool = PostgreSQLPool(config)
    await pool.create_pool()
    app.state.pool = pool  # No global variable!
    yield
    await pool.close_pool()
```

### Dependency Injection

```python
# dependencies.py
def get_pool(request: Request) -> PostgreSQLPool:
    pool = getattr(request.app.state, "pool", None)
    if pool is None:
        raise DatabaseError("PostgreSQL pool is not initialized")
    return pool

async def get_pg_connection(
    pool: Annotated[PostgreSQLPool, Depends(get_pool)],
) -> AsyncIterator[asyncpg.Connection]:
    async with pool.acquire() as connection:
        yield connection
```

### Pool Lifecycle Management

- **Startup**: Pool created in lifespan context
- **Request**: Connection acquired from pool via DI
- **Shutdown**: Pool closed gracefully

## Clean Architecture Layers

- **Domain**: Protocols for `DatabasePool`, `DatabaseConnection`
- **Infrastructure**: `PostgreSQLPool` implementation (from shared)
- **Presentation**: FastAPI endpoints, dependencies, app factory
