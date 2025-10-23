"""Version management utilities."""

import tomllib
from functools import cache
from pathlib import Path


@cache
def get_version_from_pyproject(pyproject_path: Path) -> str:
    """
    Read version from pyproject.toml file.

    Args:
        pyproject_path: Path to pyproject.toml file

    Returns:
        Version string

    Raises:
        FileNotFoundError: If pyproject.toml not found
        KeyError: If version not found in pyproject.toml
    """
    if not pyproject_path.exists():
        msg = f"pyproject.toml not found at {pyproject_path}"
        raise FileNotFoundError(msg)

    with pyproject_path.open("rb") as file:
        data = tomllib.load(file)

    try:
        return data["project"]["version"]
    except KeyError as exc:
        msg = "Version not found in pyproject.toml [project.version]"
        raise KeyError(msg) from exc
