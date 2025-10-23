"""Entry point for Task 2 application."""

import sys
from pathlib import Path

import uvicorn

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


if __name__ == "__main__":
    uvicorn.run(
        "tasks.task_2.presentation.app:create_app",
        factory=True,
        host="0.0.0.0",  # noqa: S104 - Required for Docker deployment
        port=8000,
        reload=True,
    )
