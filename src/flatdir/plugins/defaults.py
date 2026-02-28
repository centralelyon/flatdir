"""Default field plugins for flatdir.

These functions produce the built-in fields: name, type, mtime, size.
Each function receives the file path and the root directory path.
"""

from __future__ import annotations

import os
import time
from pathlib import Path


def name(path: Path, root: Path) -> str:
    """The filename or directory name (basename)."""
    return path.name


def path(path: Path, root: Path) -> str:
    """Relative path from the listing root (excluding the filename)."""
    try:
        return str(path.parent.relative_to(root))
    except ValueError:
        return str(os.path.relpath(str(path.parent), str(root)))


def type(path: Path, root: Path) -> str:
    """Entry type: 'file' or 'directory'."""
    return "directory" if path.is_dir() else "file"


def mtime(path: Path, root: Path) -> str | None:
    """Last modification time in HTTP-date format."""
    try:
        st = path.stat()
        t = time.gmtime(st.st_mtime)
        return time.strftime("%a, %d %b %Y %H:%M:%S GMT", t)
    except OSError:
        return None


def size(path: Path, root: Path) -> int | None:
    """File size in bytes. Returns None for directories (omitted from output)."""
    if path.is_dir():
        return None
    try:
        return int(path.stat().st_size)
    except OSError:
        return None
