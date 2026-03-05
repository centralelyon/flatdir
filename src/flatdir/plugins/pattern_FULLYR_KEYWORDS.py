"""Plugin: extracts information from patterns like 2022-keyword1-keyword2.

Provides fields:
  - pattern_year     : the full 4-digit year (e.g., "2022")
  - pattern_keywords : list of keyword parts after the year (e.g., ["keyword1", "keyword2"])
  - pattern_date     : the year in ISO 8601 format (e.g., "2022")
"""

from __future__ import annotations

from pathlib import Path

# Cache to avoid re-parsing the same path
_cache: dict[Path, dict[str, object] | None] = {}


def _parse_pattern(name: str) -> dict[str, object] | None:
    """Match YYYY-kw1-kw2-... and extract year + keyword list."""
    parts = name.split("-")
    if not parts:
        return None

    year_part = parts[0]
    if len(year_part) != 4 or not year_part.isdigit():
        return None

    keywords = [p for p in parts[1:] if p]

    return {
        "year": year_part,
        "keywords": keywords,
    }


def _get_parsed_data(path: Path) -> dict[str, object] | None:
    if path in _cache:
        return _cache[path]
    res = _parse_pattern(path.name)
    _cache[path] = res
    return res


def pattern_year(path: Path, root: Path) -> str | None:
    """Return the full 4-digit year (e.g., '2022')."""
    res = _get_parsed_data(path)
    return res["year"] if res else None  # type: ignore[return-value]


def pattern_keywords(path: Path, root: Path) -> list[str] | None:
    """Return the list of keywords after the year (e.g., ['keyword1', 'keyword2'])."""
    res = _get_parsed_data(path)
    return res["keywords"] if res else None  # type: ignore[return-value]


def pattern_date(path: Path, root: Path) -> str | None:
    """Return the year in ISO 8601 format (e.g., '2022')."""
    res = _get_parsed_data(path)
    return res["year"] if res else None  # type: ignore[return-value]
