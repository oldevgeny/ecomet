# ecomet

Production-ready Python microservices with Pragmatic Clean Architecture, Python 3.13, FastAPI, comprehensive testing (>90% coverage), and strict linting.

## Quick Start

```bash
# 1. Copy environment template
cp .env.example .env
# Edit .env with your database credentials and GitHub token

# 2. Install dependencies
make install

# 3. Start infrastructure (PostgreSQL + ClickHouse)
make up

# 4. Run tests to verify setup
make test

# 5. Format code before committing
make format
```

## Project Structure

This is a **uv workspace** project with:
- `shared/` - Reusable Clean Architecture components (domain protocols, infrastructure, presentation)
- `tasks/task_X/` - Independent microservices following Clean Architecture

```
ecomet/
├── shared/                 # Shared Clean Architecture library
│   ├── domain/            # Core protocols and entities
│   ├── infrastructure/    # Database clients, rate limiters, config
│   └── presentation/      # FastAPI utilities, health checks
├── tasks/
│   ├── task_1/           # PostgreSQL pool service (port 8001)
│   ├── task_2/           # GitHub scraper service (port 8002)
│   ├── task_3/           # ClickHouse integration (port 8003)
│   └── task_4/           # ClickHouse analytics (port 8004)
├── docker-compose.yml     # All services + PostgreSQL + ClickHouse
└── Makefile              # Common development commands
```

## Development

### Make Commands Reference

**Setup & Installation:**
```bash
make install              # Install all workspace dependencies (uv sync --all-packages)
make install-hooks        # Install pre-commit hooks
```

**Code Quality:**
```bash
make format               # Auto-format code with Ruff (ALWAYS before commit!)
make lint                 # Run Ruff + wemake-python-styleguide linters
make type-check          # Run Pyright type checker
make check               # Run all checks: format + lint + type-check
make pre-commit          # Run pre-commit hooks manually on all files
```

**Testing:**
```bash
make test                # Run all tests with pytest
make test-cov           # Run tests with HTML coverage report (htmlcov/)
make test-unit           # Run only unit tests
make test-integration    # Run only integration tests
```

**Docker Operations:**
```bash
make up                  # Start all services in background
make down               # Stop and remove all containers
make build              # Build and start services (rebuild images)
make restart            # Restart all services
make logs               # View logs from all services
make logs-task-1        # View logs from specific task service
make logs-task-2        # View logs from task 2
make logs-task-3        # View logs from task 3
make logs-task-4        # View logs from task 4
make logs-db            # View PostgreSQL logs
make logs-clickhouse    # View ClickHouse logs
```

**Cleanup:**
```bash
make clean              # Remove Python cache files, .pyc, __pycache__
make clean-cov          # Remove coverage reports
make clean-all          # Remove all generated files including .venv
```

**Package Management (uv workspace):**
```bash
# Add dependency to specific task
uv add --package ecomet-task-1 <package-name>

# Remove dependency
uv remove --package ecomet-task-1 <package-name>

# Sync all packages
uv sync --all-packages

# Sync specific task only
uv sync --package ecomet-task-2
```

### Running Tasks Locally

```bash
# Using uv
uv run --package ecomet-task-1 python tasks/task_1/main.py

# Using uvicorn for development
uv run uvicorn tasks.task_1.presentation.app:create_app --factory --reload --port 8001
```

## Architecture

Each task follows **Pragmatic Clean Architecture** with three layers:

1. **Domain** (`domain/`) - Pure business logic, protocols, entities
2. **Infrastructure** (`infrastructure/`) - External dependencies (DB, HTTP, etc.)
3. **Presentation** (`presentation/`) - FastAPI endpoints, DI, request/response models

Key patterns:
- No global variables (use `app.state`)
- Dependency injection via FastAPI
- Use case pattern for business logic
- Repository pattern for data access

## Services

| Service | Port | Description |
|---------|------|-------------|
| Task 1  | 8001 | PostgreSQL connection pool |
| Task 2  | 8002 | GitHub API scraper with rate limiting |
| Task 3  | 8003 | Scrape GitHub → save to ClickHouse |
| Task 4  | 8004 | ClickHouse analytics queries |
| PostgreSQL | 5432 | Database |
| ClickHouse | 9000/8123 | Analytics database |

### API Endpoints

Each service has:
- `GET /health` - Health check
- `GET /api/*` - Service-specific endpoints

## Code Quality Standards

- **Coverage**: Minimum 90%, target 95%
- **Line length**: 120 characters max
- **Linting**: Ruff + wemake-python-styleguide
- **Type checking**: Pyright
- **Pre-commit hooks**: Auto-run on commit (format, lint, test, type-check)

Install hooks: `uv run pre-commit install`

## Configuration

### Environment Variables Setup

1. **Copy the template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your credentials:**

**PostgreSQL Configuration (Required for Task 1, 2, 3):**
```bash
POSTGRES_DATABASE_URL=postgresql://user:password@localhost:5432/dbname
POSTGRES_MIN_POOL_SIZE=10        # Minimum connections in pool
POSTGRES_MAX_POOL_SIZE=20        # Maximum connections in pool
POSTGRES_POOL_TIMEOUT=30.0       # Connection acquisition timeout (seconds)
```

**ClickHouse Configuration (Required for Task 3, 4):**
```bash
CLICKHOUSE_HOST=localhost        # ClickHouse server host
CLICKHOUSE_PORT=9000            # Native protocol port
CLICKHOUSE_HTTP_PORT=8123       # HTTP interface port
CLICKHOUSE_DB=default           # Database name
CLICKHOUSE_USER=default         # Username
CLICKHOUSE_PASSWORD=            # Password (empty for default)
```

**GitHub API Configuration (Required for Task 2, 3):**
```bash
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx  # GitHub personal access token
GITHUB_MAX_CONCURRENT_REQUESTS=10              # Max parallel requests
GITHUB_REQUESTS_PER_SECOND=5                   # Rate limit (requests/sec)
```

**Task-Specific Configuration:**
```bash
# Task 1 - PostgreSQL Service
TASK_1_HOST=0.0.0.0
TASK_1_PORT=8001

# Task 2 - GitHub Scraper
TASK_2_HOST=0.0.0.0
TASK_2_PORT=8002
GITHUB_TOP_REPOS_LIMIT=100      # Number of top repos to fetch

# Task 3 - ClickHouse Integration
TASK_3_HOST=0.0.0.0
TASK_3_PORT=8003

# Task 4 - Analytics
TASK_4_HOST=0.0.0.0
TASK_4_PORT=8004
```

3. **For Docker deployment:**
   - Docker Compose uses services defined in `docker-compose.yml`
   - PostgreSQL: `localhost:5432` (user: `postgres`, password: `postgres`, db: `test`)
   - ClickHouse: `localhost:9000` (HTTP: `8123`, user: `default`, no password)

4. **Generate GitHub token:**
   - Go to https://github.com/settings/tokens/new
   - Select scopes: `public_repo` (read-only access)
   - Copy token to `GITHUB_ACCESS_TOKEN` in `.env`

## Testing

```bash
# All tests
make test

# Specific task tests
uv run pytest tasks/task_1/tests/

# Single test file
uv run pytest tasks/task_1/tests/unit/test_endpoints.py

# With coverage
make test-cov
```

## Documentation

### Project Documentation Structure

**Root Level:**
- `README.md` (this file) - Quick reference and getting started guide
- `CLAUDE.md` - Comprehensive project documentation for AI assistants and developers
  - Architecture deep dive
  - Code patterns and best practices
  - Detailed command reference
  - Testing strategies
- `.env.example` - Environment variables template with all available options

**Task Documentation:**
- `tasks/task_1/README.md` - PostgreSQL connection pool service
- `tasks/task_2/README.md` - GitHub API scraper with rate limiting
- `tasks/task_3/README.md` - ClickHouse integration and data ingestion
- `tasks/task_4/README.md` - ClickHouse analytics and aggregations

**Technical Specifications:**
- `docs/tasks_description.md` - Original task requirements and specifications
- `docs/manual_testing_latest_ru.md` - Manual testing procedures (Russian)
- `docs/Описание задач.docx` - Task descriptions (Russian, Word format)

**Database Schemas:**
- `tasks/task_3/tables.sql` - ClickHouse table definitions for task 3
- `tasks/task_4/table.sql` - ClickHouse table schema for task 4

**Configuration Files:**
- `pyproject.toml` - Workspace configuration and shared dependencies
- `ruff.toml` - Ruff linter/formatter settings (120 char line length)
- `setup.cfg` - Flake8 and wemake-python-styleguide configuration
- `.wemake.ini` - Additional wemake linter settings
- `.pre-commit-config.yaml` - Pre-commit hooks configuration
- `docker-compose.yml` - Multi-service Docker setup

### Reading Recommendations

**For Quick Start:**
1. This README (overview + commands)
2. `.env.example` (configure environment)
3. Specific task README in `tasks/task_X/`

**For Development:**
1. `CLAUDE.md` (architecture and patterns)
2. Task-specific code in `tasks/task_X/`
3. Shared library code in `shared/`

**For Understanding Requirements:**
1. `docs/tasks_description.md` (technical specs)
2. `docs/manual_testing_latest_ru.md` (testing scenarios)

## Tech Stack

- **Python**: 3.13
- **Framework**: FastAPI
- **Databases**: PostgreSQL, ClickHouse
- **Package Manager**: uv (workspace)
- **Testing**: pytest, pytest-anyio, pytest-cov
- **Linting**: Ruff, wemake-python-styleguide, Pyright
- **HTTP Client**: httpx (async)
- **Logging**: Loguru
