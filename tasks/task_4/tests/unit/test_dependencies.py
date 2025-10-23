"""Tests for Task 4 dependencies."""

from unittest.mock import MagicMock

import pytest

from shared.domain.entities.exceptions import DatabaseError
from tasks.task_4.domain.use_cases import GetPhraseViewsUseCase
from tasks.task_4.presentation.dependencies import get_use_case


class TestGetUseCase:
    """Tests for get_use_case dependency."""

    def test_get_use_case_returns_instance(self):
        request = MagicMock()
        use_case = MagicMock(spec=GetPhraseViewsUseCase)
        request.app.state.use_case = use_case

        result = get_use_case(request)
        assert result is use_case

    def test_get_use_case_raises_when_not_initialized(self):
        request = MagicMock()
        request.app.state.use_case = None

        with pytest.raises(DatabaseError, match="GetPhraseViewsUseCase is not initialized"):
            get_use_case(request)

    def test_get_use_case_raises_when_missing_attribute(self):
        request = MagicMock()
        del request.app.state.use_case

        with pytest.raises(DatabaseError, match="GetPhraseViewsUseCase is not initialized"):
            get_use_case(request)
