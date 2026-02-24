"""Plugin: returns the first character of the filename."""

from __future__ import annotations

from pathlib import Path


def starts_with(path: Path, root: Path) -> str:
    """Return the first character of the filename (e.g. '.' for hidden files)."""
    return path.name[0] if path.name else ""
