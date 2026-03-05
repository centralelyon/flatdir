"""Plugin: extracts information from patterns like 25-09-29-Aaaa-BBBBB.

Provides fields: pattern_year, pattern_month, pattern_day, pattern_low, pattern_up, pattern_date.
"""

from __future__ import annotations

import re
from pathlib import Path

# Cache to avoid re-parsing the regex for the same path
_cache: dict[Path, dict[str, str | None] | None] = {}


def _parse_generic_pattern(name: str) -> dict[str, str | None] | None:
    """A generic parser that can be adapted for similar patterns.
    
    Matches patterns like: [Year]-[Month]-[Day]-[LOW]-[UP]
    Extracts the parts.
    """
    match = re.search(r'^(\d{2})-(\d{2})-(\d{2})-([^-]+)-(.+)$', name)
    if not match:
        return None
        
    year, month, day, low, up = match.groups()
            
    return {
        "year": year,
        "month": month,
        "day": day,
        "low": low,
        "up": up,
    }


def _get_parsed_data(path: Path) -> dict[str, str | None] | None:
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
    """Return the day part of the pattern (e.g., 29)."""
    res = _get_parsed_data(path)
    return res["day"] if res else None


def pattern_low(path: Path, root: Path) -> str | None:
    """Return the LOW part of the pattern (e.g., Aaaa)."""
    res = _get_parsed_data(path)
    return res["low"] if res else None


def pattern_up(path: Path, root: Path) -> str | None:
    """Return the UP part of the pattern (e.g., BBBBB)."""
    res = _get_parsed_data(path)
    return res["up"] if res else None


def pattern_date(path: Path, root: Path) -> str | None:
    """Return the parsed date in ISO 8601 format (e.g., 2025-09-29)."""
    res = _get_parsed_data(path)
    if res is None:
        return None
    return f"20{res['year']}-{res['month']}-{res['day']}"
