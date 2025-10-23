FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

COPY ../../uv.lock ../../pyproject.toml ./
COPY tasks/task_4/pyproject.toml tasks/task_4/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY shared/ shared/
COPY tasks/__init__.py tasks/
COPY tasks/task_4/ tasks/task_4/

# Copy task-specific .env file
# Using wildcard pattern [v] to make COPY optional (won't fail if file doesn't exist)
COPY tasks/task_4/.en[v] ./.env* ./

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["python", "tasks/task_4/main.py"]
