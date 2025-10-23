"""FastAPI dependencies for Task 4."""

from fastapi import Request

from shared.domain.entities.exceptions import DatabaseError
from tasks.task_4.domain.use_cases import GetPhraseViewsUseCase


def get_use_case(request: Request) -> GetPhraseViewsUseCase:
    """
    Get phrase views use case from app state.

    Args:
        request: FastAPI request object

    Returns:
        GetPhraseViewsUseCase instance

    Raises:
        DatabaseError: If use case is not initialized
    """
    use_case = getattr(request.app.state, "use_case", None)
    if use_case is None:
        msg = "GetPhraseViewsUseCase is not initialized"
        raise DatabaseError(msg)
    return use_case
