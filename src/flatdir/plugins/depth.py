"""Plugin: returns the depth (number of directories) relative to the root."""

from __future__ import annotations

from pathlib import Path


def depth(path: Path, root: Path) -> int:
    """Return the depth of the file relative to the listed root directory.
    
    The root directory itself (if listed) is depth 0. Files directly inside
    the root directory are depth 1.
    """
    try:
        return len(path.relative_to(root).parts)
    except ValueError:
        # Fallback if path is not relative to root somehow
        import os
        return len(Path(os.path.relpath(path, root)).parts)
