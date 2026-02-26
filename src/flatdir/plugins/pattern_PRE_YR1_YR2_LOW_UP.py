"""Plugin: extracts information from patterns like ABC-19-20-aa-BB-BB.

Provides fields: pattern_prefix, pattern_year1, pattern_year2, pattern_lower, pattern_upper.
"""

from __future__ import annotations

import re
from pathlib import Path

# Cache to avoid re-parsing the regex for the same path
_cache: dict[Path, dict[str, str | None] | None] = {}


def _parse_generic_pattern(name: str) -> dict[str, str | None] | None:
    """A generic parser that can be adapted for similar patterns.
    
    Matches patterns like: [Prefix]-[Year1]-[Year2]-[Remaining Parts]
    Extracts the parts and separates remaining ones into lower/upper cases.
    """
    match = re.search(r'^([A-Za-z]+)-(\d{2})-(\d{2})-(.*)$', name)
    if not match:
        return None
        
    prefix, year1, year2, rest = match.groups()
    parts = rest.split('-')
    
    lower_parts = []
    upper_parts = []
    
    for p in parts:
        if p.islower():
            lower_parts.append(p)
        elif p.isupper():
            upper_parts.append(p)
            
    return {
        "prefix": prefix,
        "year1": year1,
        "year2": year2,
        "lower": "-".join(lower_parts) if lower_parts else None,
        "upper": "-".join(upper_parts) if upper_parts else None,
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


def pattern_lower(path: Path, root: Path) -> str | None:
    """Return the lowercase part of the pattern."""
    res = _get_parsed_data(path)
    return res["lower"] if res else None


def pattern_upper(path: Path, root: Path) -> str | None:
    """Return the uppercase part of the pattern."""
    res = _get_parsed_data(path)
    return res["upper"] if res else None
