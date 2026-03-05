"""Plugin: extracts postfixes and extensions from files within a directory matching the directory name.
"""

from __future__ import annotations

from pathlib import Path


def has_postfix(path: Path, root: Path) -> list[str] | None:
    """Return a list of postfixes for files matching `{dirname}_{postfix}.{ext}` in a directory.
    
    If `path` is a file, returns None.
    If `path` is a directory, it scans its immediate children.
    For a directory named "toto", a file named "toto_tata.json" yields the postfix "tata".
    Returns a sorted list of unique postfixes.
    """
    if not path.is_dir():
        return None

    dirname = path.name
    postfixes = set()
    prefix = f"{dirname}_"

    try:
        for child in path.iterdir():
            if not child.is_file():
                continue
            
            filename = child.stem
            if filename.startswith(prefix) and len(filename) > len(prefix):
                postfix = filename[len(prefix):]
                postfixes.add(postfix)
    except OSError:
        pass

    return sorted(list(postfixes))


def has_ext(path: Path, root: Path) -> list[str] | None:
    """Return a list of extensions for files matching `{dirname}.{ext}` or `{dirname}_{postfix}.{ext}` in a directory.
    
    If `path` is a file, returns None.
    If `path` is a directory, it scans its immediate children.
    For a directory named "toto", files "toto.json" and "toto_tata.xml" yield extensions "json" and "xml".
    Returns a sorted list of unique extensions without the leading dot.
    """
    if not path.is_dir():
        return None

    dirname = path.name
    extensions = set()
    prefix = f"{dirname}_"
    exact_match = dirname

    try:
        for child in path.iterdir():
            if not child.is_file():
                continue
            
            filename = child.stem
            ext = child.suffix.lstrip('.')
            
            if not ext:
                continue

            if filename == exact_match or (filename.startswith(prefix) and len(filename) > len(prefix)):
                extensions.add(ext)
    except OSError:
        pass

    return sorted(list(extensions))
