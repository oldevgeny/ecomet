"""FastAPI dependencies for Task 3."""

from fastapi import Request

from shared.domain.entities.exceptions import ScraperError
from tasks.task_3.domain.use_cases import ScrapAndSaveUseCase


def get_use_case(request: Request) -> ScrapAndSaveUseCase:
    """
    Get scrape and save use case from app state.

    Args:
        request: FastAPI request object

    Returns:
        ScrapAndSaveUseCase instance

    Raises:
        ScraperError: If use case is not initialized
    """
    use_case = getattr(request.app.state, "use_case", None)
    if use_case is None:
        msg = "ScrapAndSaveUseCase is not initialized"
        raise ScraperError(msg)
    return use_case
