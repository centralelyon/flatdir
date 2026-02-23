"""Plugin: adds the file extension to each entry."""

from __future__ import annotations

from pathlib import Path


def ext(path: Path, root: Path) -> str | None:
    """Return the file extension (e.g. '.csv', '.mp4'). None for directories."""
    if path.is_dir():
        return None
    return path.suffix.lower() if path.suffix else ""
