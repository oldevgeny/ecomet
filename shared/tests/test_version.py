"""Tests for version management utilities."""

from pathlib import Path

import pytest

from shared.infrastructure.version import get_version_from_pyproject


def test_get_version_from_existing_pyproject() -> None:
    """Test reading version from existing pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    version = get_version_from_pyproject(pyproject_path)
    assert version == "0.1.0"


def test_get_version_from_task_pyproject() -> None:
    """Test reading version from task's pyproject.toml."""
    task1_path = Path(__file__).parent.parent.parent / "tasks/task_1/pyproject.toml"
    version = get_version_from_pyproject(task1_path)
    assert version == "0.1.0"


def test_get_version_caching() -> None:
    """Test that version reading is cached."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

    # Call twice and verify it's the same instance (cached)
    version1 = get_version_from_pyproject(pyproject_path)
    version2 = get_version_from_pyproject(pyproject_path)

    assert version1 is version2


def test_get_version_from_nonexistent_file() -> None:
    """Test error handling for missing pyproject.toml."""
    nonexistent_path = Path("/nonexistent/pyproject.toml")

    with pytest.raises(FileNotFoundError, match="pyproject.toml not found"):  # noqa: RUF043
        get_version_from_pyproject(nonexistent_path)
