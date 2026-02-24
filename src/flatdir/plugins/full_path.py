"""Plugin: returns the absolute full path of the entry."""

from __future__ import annotations

from pathlib import Path


def full_path(path: Path, root: Path) -> str:
    """Return the absolute path of the file or directory."""
    return str(path.resolve())
