"""Plugin: extracts a sequence_id and sequence_name from a prefix like 00_name or 01_document.

Provides fields: sequence_id, sequence_name.
"""

from __future__ import annotations

import re
from pathlib import Path

_cache: dict[Path, dict[str, int | str | None] | None] = {}


def _get_parsed_data(path: Path) -> dict[str, int | str | None] | None:
    if path in _cache:
        return _cache[path]
        
    match = re.search(r'^([0-9]+)_(.*)$', path.name)
    if not match:
        _cache[path] = None
        return None
        
    raw_str = match.group(1)
    name_part = match.group(2)
    
    # Calculate number of leading zeros
    if raw_str == '0' * len(raw_str):
        # e.g., "00" has 1 leading zero before the actual "0" value
        leading_zeros = max(0, len(raw_str) - 1)
    else:
        leading_zeros = len(raw_str) - len(raw_str.lstrip('0'))
        
    if leading_zeros > 10:
        _cache[path] = None
        return None
        
    res_id = int(raw_str)
    
    res = {
        "sequence_id": res_id,
        "sequence_name": name_part
    }
    _cache[path] = res
    return res


def sequence_id(path: Path, root: Path) -> int | None:
    """Return the sequence ID parsed from the beginning of the name (e.g. 01_ -> 1).
    
    Supports up to 10 zero left padding.
    """
    res = _get_parsed_data(path)
    return res["sequence_id"] if res else None


def sequence_name(path: Path, root: Path) -> str | None:
    """Return the remainder of the filename after the sequence ID and underscore."""
    res = _get_parsed_data(path)
    # The dictionary value is typed as `int | str | None`, so type checker might complain 
    # if we don't explicitly cast/promise it's a string, but it's fine for duck typing.
    return res["sequence_name"] if res else None  # type: ignore
