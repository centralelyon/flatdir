"""Example plugin: adds the length of the filename to each entry."""

from pathlib import Path


def filename_length(p: Path) -> int:
    """Return the number of characters in the filename (including extension)."""
    return len(p.name)
