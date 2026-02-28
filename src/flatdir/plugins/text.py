"""Plugin to extract text-specific properties (line count, word count, character count) from text files."""

from __future__ import annotations

import collections
from pathlib import Path

# Common plain-text extensions to process. Everything else will be ignored.
TEXT_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".xml", ".html", ".css", ".js", ".ts", 
    ".py", ".sh", ".yaml", ".yml", ".ini", ".cfg", ".log"
}

# In-memory cache to prevent reading the same file multiple times
# when calculating different fields sequentially.
_cache: dict[Path, str] = {}


def _get_text(path: Path) -> str | None:
    """Helper to safely read and cache text content."""
    if path.is_dir() or path.suffix.lower() not in TEXT_EXTENSIONS:
        return None
        
    if path in _cache:
        return _cache[path]
        
    try:
        content = path.read_text(encoding="utf-8")
        _cache[path] = content
        return content
    except (UnicodeDecodeError, OSError):
        return None


def text_characters(path: Path, root: Path) -> int | None:
    """Return the total number of characters in the file."""
    content = _get_text(path)
    if content is None:
        return None
    return len(content)


def text_words(path: Path, root: Path) -> int | None:
    """Return the total number of words in the file."""
    content = _get_text(path)
    if content is None:
        return None
    return len(content.split())


def text_lines(path: Path, root: Path) -> int | None:
    """Return the total number of lines in the file."""
    content = _get_text(path)
    if content is None:
        return None
    return len(content.splitlines())


def text_is_blank(path: Path, root: Path) -> bool | None:
    """Return True if the text file only contains whitespace or is empty."""
    content = _get_text(path)
    if content is None:
        return None
    return not content.strip()
