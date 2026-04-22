"""Plugin: list immediate child directories, optionally filtered by a CLI whitelist."""

from __future__ import annotations

from pathlib import Path

from flatdir.plugins import options


def subfolders(path: Path, root: Path) -> list[str] | None:
    if not path.is_dir():
        return None

    try:
        folders = [child.name for child in path.iterdir() if child.is_dir()]
    except OSError:
        return None

    if options.subfolders_whitelist:
        allowed = set(options.subfolders_whitelist)
        folders = [name for name in folders if name in allowed]

    return sorted(folders)
