"""Plugin: extracts information from patterns like 25-09-06-AAA-BBB-CCC.

Provides fields: pattern_year, pattern_month, pattern_day, pattern_kw, parsed_date.
"""

from __future__ import annotations

import re
from pathlib import Path

# Cache to avoid re-parsing the regex for the same path
_cache: dict[Path, dict[str, str | list[str] | None] | None] = {}


def _parse_generic_pattern(name: str) -> dict[str, str | list[str] | None] | None:
    """A parser for YY-MM-DD-KW1-KW2 patterns.
    
    Extracts the parts and groups the rest into keywords.
    """
    match = re.search(r'^(\d{2})-(\d{2})-(\d{2})-(.+)$', name)
    if not match:
        return None
        
    year, month, day, rest = match.groups()
    keywords = rest.split('-')
            
    return {
        "year": year,
        "month": month,
        "day": day,
        "kw": keywords,
        "parsed_date": f"20{year}-{month}-{day}"
    }


def _get_parsed_data(path: Path) -> dict[str, str | list[str] | None] | None:
    if path in _cache:
        return _cache[path]
    
    res = _parse_generic_pattern(path.name)
    _cache[path] = res
    return res


def pattern_year(path: Path, root: Path) -> str | None:
    """Return the year part of the pattern (e.g., 25)."""
    res = _get_parsed_data(path)
    return res["year"] if res else None


def pattern_month(path: Path, root: Path) -> str | None:
    """Return the month part of the pattern (e.g., 09)."""
    res = _get_parsed_data(path)
    return res["month"] if res else None


def pattern_day(path: Path, root: Path) -> str | None:
    """Return the day part of the pattern (e.g., 06)."""
    res = _get_parsed_data(path)
    return res["day"] if res else None


def pattern_kw(path: Path, root: Path) -> list[str] | None:
    """Return the keywords as a list of strings."""
    res = _get_parsed_data(path)
    return res["kw"] if res else None


def parsed_date(path: Path, root: Path) -> str | None:
    """Return the parsed date in ISO 8601 format (e.g., 2025-09-06)."""
    res = _get_parsed_data(path)
    return res["parsed_date"] if res else None
