"""Plugin: extracts information from patterns like PE-25-26-70-Competition.

Provides fields: pattern_prefix, pattern_year1, pattern_year2, pattern_id, pattern_name.
"""

from __future__ import annotations

import re
from pathlib import Path

# Cache to avoid re-parsing the regex for the same path
_cache: dict[Path, dict[str, str | None] | None] = {}


def _parse_generic_pattern(name: str) -> dict[str, str | None] | None:
    """A generic parser that can be adapted for similar patterns.
    
    Matches patterns like: [Prefix]-[Year1]-[Year2]-[ID]-[Name].
    ID can be a single number or a numeric ID string such as 105_106.
    Extracts the parts.
    """
    match = re.search(r'^([A-Za-z0-9]+)-(\d{2})-(\d{2})-(\d+(?:[-_+,.]\d+)*)-(.+)$', name)
    if not match:
        return None
        
    prefix, year1, year2, id_val, name_val = match.groups()
            
    return {
        "prefix": prefix,
        "year1": year1,
        "year2": year2,
        "id": id_val,
        "name": name_val,
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
    """Return the first year part of the pattern (e.g., 25)."""
    res = _get_parsed_data(path)
    return res["year1"] if res else None


def pattern_year2(path: Path, root: Path) -> str | None:
    """Return the second year part of the pattern (e.g., 26)."""
    res = _get_parsed_data(path)
    return res["year2"] if res else None


def pattern_id(path: Path, root: Path) -> str | None:
    """Return the ID part of the pattern (e.g., 70)."""
    res = _get_parsed_data(path)
    return res["id"] if res else None


def pattern_name(path: Path, root: Path) -> str | None:
    """Return the suffix name part of the pattern (e.g., Competition)."""
    res = _get_parsed_data(path)
    return res["name"] if res else None
