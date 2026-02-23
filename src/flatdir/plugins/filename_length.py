"""Example plugin: adds the length of the filename to each entry."""

from __future__ import annotations

from pathlib import Path


def filename_length(path: Path, root: Path) -> int:
    """Return the number of characters in the filename (including extension)."""
    return len(path.name)
