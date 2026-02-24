"""Plugin: returns the parent directory of the entry."""

from __future__ import annotations

from pathlib import Path


def parent(path: Path, root: Path) -> str:
    """Return the parent directory of the file or directory, relative to root."""
    try:
        # If the path is the root itself, parent is "."
        if path.resolve() == root.resolve():
            return "."
        return str(path.parent.relative_to(root))
    except ValueError:
        import os
        return str(os.path.relpath(path.parent, root))
