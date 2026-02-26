"""Plugin: extracts PRE-YR1-YR2 pattern information from the parent directory.

Provides fields: parent_pattern_prefix, parent_pattern_year1, parent_pattern_year2.
This is useful for filtering entries based on the properties of their parent directory.
"""

from __future__ import annotations

import re
from pathlib import Path

# Cache to avoid re-parsing the regex for the same parent path
_cache: dict[Path, dict[str, str | None] | None] = {}


def _parse_generic_pattern(name: str) -> dict[str, str | None] | None:
    """A generic parser for [Prefix]-[Year1]-[Year2]."""
    match = re.search(r'^([A-Za-z0-9]+)-(\d{2})-(\d{2})$', name)
    if not match:
        return None
        
    prefix, year1, year2 = match.groups()
            
    return {
        "parent_prefix": prefix,
        "parent_year1": year1,
        "parent_year2": year2,
    }


def _get_parsed_data(path: Path) -> dict[str, str | None] | None:
    parent_path = path.parent
    if parent_path in _cache:
        return _cache[parent_path]
    
    res = _parse_generic_pattern(parent_path.name)
    _cache[parent_path] = res
    return res


def parent_pattern_prefix(path: Path, root: Path) -> str | None:
    """Return the prefix of the parent directory's pattern."""
    res = _get_parsed_data(path)
    return res["parent_prefix"] if res else None


def parent_pattern_year1(path: Path, root: Path) -> str | None:
    """Return the first year part of the parent directory's pattern."""
    res = _get_parsed_data(path)
    return res["parent_year1"] if res else None


def parent_pattern_year2(path: Path, root: Path) -> str | None:
    """Return the second year part of the parent directory's pattern."""
    res = _get_parsed_data(path)
    return res["parent_year2"] if res else None
