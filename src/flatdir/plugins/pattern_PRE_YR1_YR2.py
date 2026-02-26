"""Plugin: extracts information from patterns like ABC-19-20.

Provides fields: pattern_prefix, pattern_year1, pattern_year2.
"""

from __future__ import annotations

import re
from pathlib import Path

# Cache to avoid re-parsing the regex for the same path
_cache: dict[Path, dict[str, str | None] | None] = {}


def _parse_generic_pattern(name: str) -> dict[str, str | None] | None:
    """A generic parser that can be adapted for similar patterns.
    
    Matches patterns like: [Prefix]-[Year1]-[Year2]
    Extracts the parts.
    """
    match = re.search(r'^([A-Za-z0-9]+)-(\d{2})-(\d{2})$', name)
    if not match:
        return None
        
    prefix, year1, year2 = match.groups()
            
    return {
        "prefix": prefix,
        "year1": year1,
        "year2": year2,
    }


def _get_parsed_data(path: Path) -> dict[str, str | None] | None:
    if path in _cache:
        return _cache[path]
    
    res = _parse_generic_pattern(path.name)
    _cache[path] = res
    return res


def pattern_prefix(path: Path, root: Path) -> str | None:
    """Return the strict first letters of the pattern."""
    res = _get_parsed_data(path)
    return res["prefix"] if res else None


def pattern_year1(path: Path, root: Path) -> str | None:
    """Return the first year part of the pattern (e.g., 19)."""
    res = _get_parsed_data(path)
    return res["year1"] if res else None


def pattern_year2(path: Path, root: Path) -> str | None:
    """Return the second year part of the pattern (e.g., 20)."""
    res = _get_parsed_data(path)
    return res["year2"] if res else None
